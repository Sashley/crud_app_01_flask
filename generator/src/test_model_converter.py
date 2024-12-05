import os
import shutil
from .model_converter import SQLAlchemyModelParser, ModelConfigGenerator

def test_conversion():
    """Test the model conversion process"""
    # Setup
    source_file = '../../meta/m01/models.py'
    output_dir = 'generator/output'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    try:
        # Parse models
        parser = SQLAlchemyModelParser(source_file)
        parser.parse_models()
        
        # Verify basic parsing
        assert len(parser.models) > 0, "No models were parsed"
        assert 'Manifest' in parser.models, "Manifest model not found"
        assert 'LineItem' in parser.models, "LineItem model not found"
        
        # Generate configs
        generator = ModelConfigGenerator(parser)
        configs = generator.generate_configs()
        
        # Verify config generation
        assert len(configs) > 0, "No configs were generated"
        assert 'manifest' in configs, "Manifest config not generated"
        assert 'lineitem' in configs, "LineItem config not generated"
        
        # Verify specific fields
        manifest_config = configs['manifest']
        assert any(f.name == 'bill_of_lading' for f in manifest_config.fields), "bill_of_lading field not found"
        assert any(f.name == 'shipper_id' and f.field_type.value == 'foreign_key' 
                  for f in manifest_config.fields), "shipper_id foreign key not found"
        
        print("\n✓ Model conversion tests passed")
        print(f"\nGenerated {len(configs)} model configurations:")
        for table_name, config in configs.items():
            print(f"- {config.name}: {len(config.fields)} fields")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_conversion()
