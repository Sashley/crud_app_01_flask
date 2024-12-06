import os
import importlib.util
import inspect
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.orm import RelationshipProperty
from database import Base, init_db
from flask import render_template

def load_module(file_path):
    """Load a Python module from file path."""
    print(f"Loading module from: {file_path}")
    try:
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module {file_path}: {str(e)}")
        return None

def get_relationships(model_class):
    """Extract relationships from a SQLAlchemy model class."""
    print(f"Analyzing relationships for: {model_class.__name__}")
    try:
        mapper = sqlalchemy_inspect(model_class)
        relationships = []
        
        # Get foreign keys
        for column in mapper.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    target_table = fk.column.table.name
                    target_model = target_table.title().replace('_', '')
                    relationships.append({
                        'name': column.name,
                        'target': target_model,
                        'type': 'many-to-one'  # Foreign keys typically indicate many-to-one relationships
                    })
        
        return relationships
    except Exception as e:
        print(f"Error getting relationships for {model_class.__name__}: {str(e)}")
        return []

def analyze_models():
    """Analyze all models and their relationships."""
    models_dir = os.path.join('generator', 'output', 'models')
    relationship_tree = {}
    model_classes = {}
    
    print(f"\nScanning models directory: {models_dir}")
    
    # Get all Python files in the models directory
    model_files = [f for f in os.listdir(models_dir) 
                  if f.endswith('.py') and not f.startswith('__')]
    
    print(f"Found model files: {model_files}")
    
    # First pass: Import all model classes
    print("\nFirst pass: Importing all model classes")
    for model_file in sorted(model_files):  # Sort to ensure consistent import order
        file_path = os.path.join(models_dir, model_file)
        try:
            module = load_module(file_path)
            if module:
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Base) and 
                        obj != Base):
                        print(f"Imported model class: {name}")
                        model_classes[name] = obj
        except Exception as e:
            print(f"Error importing {model_file}: {str(e)}")
    
    # Initialize SQLAlchemy after importing all models
    print("\nInitializing SQLAlchemy...")
    init_db()
    
    # Second pass: Analyze relationships
    print("\nSecond pass: Analyzing relationships")
    for name, model_class in model_classes.items():
        try:
            relationships = get_relationships(model_class)
            if relationships:
                relationship_tree[name] = relationships
                print(f"Added relationships for {name}: {relationships}")
        except Exception as e:
            print(f"Error analyzing {name}: {str(e)}")
    
    return relationship_tree

def register_routes(app):
    """Register the relationship tree routes with Flask."""
    @app.route('/relationship_tree')
    def relationship_tree():
        tree = analyze_models()
        return render_template('relationship_tree.html', relationship_tree=tree)

def main():
    """Main function to generate the relationship tree."""
    print("Starting relationship tree generation...")
    relationship_tree = analyze_models()
    
    if relationship_tree:
        print("\nGenerated relationship tree structure:")
        for model, rels in relationship_tree.items():
            print(f"\n{model}:")
            for rel in rels:
                print(f"  - {rel['name']} -> {rel['target']} ({rel['type']})")
        
        print("\nRelationship tree generation completed successfully!")
    else:
        print("\nNo relationships found in the models!")

if __name__ == '__main__':
    main()
