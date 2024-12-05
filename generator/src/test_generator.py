import os
import shutil
from .model_config import ModelConfig, Field, FieldType, RelationType, model_registry
from .model_generator import ModelGenerator
import traceback

def test_single_model():
    """Test generator with a single model configuration"""
    try:
        # Clean up any existing generated files
        output_dir = 'generator/output'
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        # Create necessary directories
        os.makedirs(f'{output_dir}/models', exist_ok=True)
        os.makedirs(f'{output_dir}/routes', exist_ok=True)
        os.makedirs(f'{output_dir}/templates', exist_ok=True)
        
        # Use the manifest config as a test case
        generator = ModelGenerator({"manifest": model_registry["manifest"]})
        generator.generate_all()
        
        print("✓ Successfully generated files for manifest model")
        print("\nGenerated files:")
        print(f"- {output_dir}/models/manifest.py")
        print(f"- {output_dir}/routes/manifest_routes.py")
        print(f"- {output_dir}/templates/manifest/list.html")
        print(f"- {output_dir}/templates/manifest/form.html")
        
        # Read and print the generated model
        with open(f'{output_dir}/models/manifest.py', 'r') as f:
            print("\nGenerated model:")
            print(f.read())
        
        print("\nNext steps:")
        print("1. Review the generated files")
        print("2. Test the manifest model routes")
        print("3. If successful, proceed with generating other models")
        print("\nTo test the manifest routes:")
        print("1. Import the generated routes in app.py")
        print("2. Start the Flask server")
        print("3. Visit http://localhost:5000/manifest")
        
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_single_model()
