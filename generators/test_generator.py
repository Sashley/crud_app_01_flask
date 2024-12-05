import os
import shutil
from config import ModelConfig, Field, FieldType, RelationType, model_registry
from generators.model_generator import ModelGenerator
import traceback

def generate_test_models():
    try:
        # Clear existing generated files
        if os.path.exists("generated_models"):
            shutil.rmtree("generated_models")
        if os.path.exists("generated_routes"):
            shutil.rmtree("generated_routes")
            
        os.makedirs("generated_models", exist_ok=True)
        os.makedirs("generated_routes", exist_ok=True)
        
        # Initialize generator
        generator = ModelGenerator()
        
        # Generate models from registry
        for model_name, config in model_registry.items():
            generator.generate_model(config)
            generator.generate_routes(config)
            
        print("Test models generated successfully!")
        
    except Exception as e:
        print(f"Error generating test models: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    generate_test_models()
