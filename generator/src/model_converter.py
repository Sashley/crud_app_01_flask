from typing import Dict, List, Optional, Tuple
import ast
import sys
import json
from dataclasses import asdict
from enum import Enum
from .model_config import ModelConfig, Field, FieldType, RelationType

class SQLAlchemyModelParser:
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.models: Dict[str, dict] = {}
        self.relationships: Dict[str, List[dict]] = {}  # model -> [{field, target, type, back_populates, foreign_keys}]
        self.model_nodes = {}  # Store AST nodes for cross-referencing
        self.model_names = {}  # Map tablename to class name
        
    def parse_models(self) -> None:
        """Parse SQLAlchemy models from the source file"""
        with open(self.source_file, 'r') as f:
            tree = ast.parse(f.read())
            
        # First pass: collect all models and their tablenames
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(base.id == 'Base' for base in node.bases if isinstance(base, ast.Name)):
                    self.model_nodes[node.name] = node
                    self.models[node.name] = {
                        'tablename': None,
                        'fields': [],
                        'relationships': []
                    }
                    self.relationships[node.name] = []
        
        # Second pass: parse each model
        for model_name, node in self.model_nodes.items():
            self._parse_model(model_name, node)
            
        # Store model names mapping
        for model_name, model_data in self.models.items():
            if model_data['tablename']:
                self.model_names[model_data['tablename']] = model_name
        
        # Third pass: resolve back references
        self._resolve_back_references()
    
    def _parse_model(self, model_name: str, node: ast.ClassDef) -> None:
        """Parse a single SQLAlchemy model class"""
        for item in node.body:
            # Get tablename
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '__tablename__':
                        if isinstance(item.value, ast.Constant):
                            self.models[model_name]['tablename'] = item.value.value
            
            # Get columns and relationships
            if isinstance(item, ast.Assign):
                if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                    field_name = item.targets[0].id
                    value = item.value
                    
                    if isinstance(value, ast.Call):
                        if isinstance(value.func, ast.Name):
                            # Handle Column definitions
                            if value.func.id == 'Column':
                                field = self._parse_column(value)
                                if field:
                                    self.models[model_name]['fields'].append((field_name, field))
                        
                        elif isinstance(value.func, ast.Name) and value.func.id == 'relationship':
                            # Handle relationship definitions
                            rel = self._parse_relationship(model_name, field_name, value)
                            if rel:
                                self.relationships[model_name].append(rel)
    
    def _parse_column(self, node: ast.Call) -> Optional[dict]:
        """Parse a Column definition"""
        field = {'type': None, 'nullable': True, 'primary_key': False, 'foreign_key': None}
        
        for arg in node.args:
            if isinstance(arg, ast.Name):
                field['type'] = arg.id
            elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                if arg.func.id == 'ForeignKey':
                    if isinstance(arg.args[0], ast.Constant):
                        field['foreign_key'] = arg.args[0].value
        
        for kw in node.keywords:
            if kw.arg == 'nullable':
                if isinstance(kw.value, ast.Constant):
                    field['nullable'] = kw.value.value
            elif kw.arg == 'primary_key':
                if isinstance(kw.value, ast.Constant):
                    field['primary_key'] = kw.value.value
        
        return field
    
    def _parse_relationship(self, model_name: str, field_name: str, node: ast.Call) -> Optional[dict]:
        """Parse a relationship definition"""
        if not node.args:
            return None
            
        if isinstance(node.args[0], ast.Constant):
            target_model = node.args[0].value
            relationship_type = "many_to_one"  # Default
            back_populates = None
            foreign_keys = []
            
            for kw in node.keywords:
                if kw.arg == 'back_populates':
                    if isinstance(kw.value, ast.Constant):
                        back_populates = kw.value.value
                        relationship_type = "one_to_many"
                elif kw.arg == 'uselist':
                    if isinstance(kw.value, ast.Constant) and not kw.value.value:
                        relationship_type = "one_to_one"
                elif kw.arg == 'foreign_keys':
                    if isinstance(kw.value, ast.List):
                        for elt in kw.value.elts:
                            if isinstance(elt, ast.Attribute):
                                # Handle Model.field_name
                                if isinstance(elt.value, ast.Name):
                                    foreign_keys.append(elt.attr)
                            elif isinstance(elt, ast.Name):
                                # Handle direct field name
                                foreign_keys.append(elt.id)
            
            # If no foreign_keys specified, try to infer from field name
            if not foreign_keys:
                inferred_fk = f"{field_name}_id"
                foreign_keys.append(inferred_fk)
            
            return {
                'model': model_name,
                'field': field_name,
                'target': target_model,
                'type': relationship_type,
                'back_populates': back_populates,
                'foreign_keys': foreign_keys
            }
        return None
    
    def _resolve_back_references(self):
        """Resolve bidirectional relationships"""
        # Create a map of back_populates references
        back_refs = {}
        for model_name, rels in self.relationships.items():
            for rel in rels:
                if rel['back_populates']:
                    key = (rel['target'], rel['back_populates'])
                    back_refs[key] = (model_name, rel['field'], rel['type'])
        
        # Update relationship types based on back references
        for model_name, rels in self.relationships.items():
            for rel in rels:
                key = (model_name, rel['field'])
                if key in back_refs:
                    # This is the target of a back-populated relationship
                    back_model, back_field, back_type = back_refs[key]
                    # Reverse the relationship type
                    if back_type == 'one_to_many':
                        rel['type'] = 'many_to_one'
                    elif back_type == 'many_to_one':
                        rel['type'] = 'one_to_many'

class ModelConfigGenerator:
    def __init__(self, parser: SQLAlchemyModelParser):
        self.parser = parser
        
    def _get_field_type(self, sa_type: str) -> FieldType:
        """Convert SQLAlchemy type to FieldType"""
        type_map = {
            'String': FieldType.STRING,
            'Integer': FieldType.INTEGER,
            'Float': FieldType.FLOAT,
            'DateTime': FieldType.DATETIME
        }
        return type_map.get(sa_type, FieldType.STRING)
    
    def _get_relation_type(self, rel_type: str) -> RelationType:
        """Convert relationship type string to RelationType"""
        type_map = {
            'one_to_many': RelationType.ONE_TO_MANY,
            'many_to_one': RelationType.MANY_TO_ONE,
            'one_to_one': RelationType.ONE_TO_ONE
        }
        return type_map.get(rel_type, RelationType.MANY_TO_ONE)
    
    def generate_configs(self) -> Dict[str, ModelConfig]:
        """Generate ModelConfig objects for all models"""
        configs = {}
        
        # First pass: create basic configs with fields
        for model_name, model_data in self.parser.models.items():
            fields = []
            
            # Add regular fields
            for field_name, field_data in model_data['fields']:
                if field_data['foreign_key']:
                    field_type = FieldType.FOREIGN_KEY
                else:
                    field_type = self._get_field_type(field_data['type'])
                
                field = Field(
                    name=field_name,
                    field_type=field_type,
                    nullable=field_data['nullable'],
                    foreign_key=field_data['foreign_key'],
                )
                fields.append(field)
            
            config = ModelConfig(
                name=model_name,
                table_name=model_data['tablename'],
                display_name=model_name.replace('_', ' ').title(),
                fields=fields,
                list_display=[f.name for f in fields if not f.name == 'id'][:5],
                search_fields=[f.name for f in fields if f.field_type == FieldType.STRING][:3],
                order_by=['-id']
            )
            
            configs[model_data['tablename']] = config
        
        # Second pass: add relationships
        for model_name, relationships in self.parser.relationships.items():
            if model_name not in self.parser.models:
                continue
                
            table_name = self.parser.models[model_name]['tablename']
            config = configs[table_name]
            
            for rel in relationships:
                # Update foreign key fields with relationship info
                for fk in rel['foreign_keys']:
                    existing_field = next((f for f in config.fields if f.name == fk), None)
                    if existing_field:
                        existing_field.relationship = self._get_relation_type(rel['type'])
                
                # Get the target model's table name from the model name
                target_model = rel['target']
                target_table = None
                for model, data in self.parser.models.items():
                    if model == target_model:
                        target_table = data['tablename']
                        break
                
                if target_table:
                    # Add relationship field
                    field = Field(
                        name=rel['field'],
                        field_type=FieldType.FOREIGN_KEY,
                        relationship=self._get_relation_type(rel['type']),
                        foreign_key=f"{target_table}.id"  # Use the actual table name
                    )
                    config.fields.append(field)
        
        return configs

def generate_summary(configs: Dict[str, ModelConfig]) -> dict:
    """Generate a summary of the configurations for continuation"""
    summary = {
        'models': {},
        'relationships': []
    }
    
    for table_name, config in configs.items():
        # Summarize model fields
        fields_summary = []
        relationships = []
        
        for field in config.fields:
            # Convert field to dict and handle enum values
            field_dict = {
                'name': field.name,
                'field_type': field.field_type.value if field.field_type else None,
                'nullable': field.nullable,
                'foreign_key': field.foreign_key,
                'relationship': field.relationship.value if field.relationship else None,
                'validation': field.validation
            }
            
            if field.foreign_key or field.relationship:
                relationships.append(field_dict)
            fields_summary.append(field_dict)
        
        summary['models'][table_name] = {
            'name': config.name,
            'fields': fields_summary
        }
        
        if relationships:
            summary['relationships'].extend(relationships)
    
    return summary

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python -m generator.src.model_converter <source_file> [--test]")
        sys.exit(1)
    
    source_file = sys.argv[1]
    test_mode = "--test" in sys.argv
    
    # Parse models and generate configs
    parser = SQLAlchemyModelParser(source_file)
    parser.parse_models()
    
    generator = ModelConfigGenerator(parser)
    configs = generator.generate_configs()
    
    # Generate summary
    summary = generate_summary(configs)
    
    # Save summary for continuation
    with open('generator/model_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    if test_mode:
        # In test mode, generate one model and verify
        test_model = next(iter(configs.values()))
        from .model_generator import ModelGenerator
        test_generator = ModelGenerator({test_model.table_name: test_model})
        test_generator.generate_all()
        print(f"Generated test files for model: {test_model.name}")
    else:
        # Generate all models
        from .model_generator import ModelGenerator
        generator = ModelGenerator(configs)
        generator.generate_all()
        print(f"Generated files for {len(configs)} models")
    
    print(f"\nGenerated summary saved to generator/model_summary.json")
    print("Summary contains:")
    print(f"- {len(summary['models'])} models")
    print(f"- {len(summary['relationships'])} relationships")

if __name__ == '__main__':
    main()
