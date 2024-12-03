import os
import shutil
from model_config import ModelConfig, Field, FieldType, RelationType, model_registry
from model_generator import ModelGenerator
import traceback

def test_single_model():
    """Test generator with a single model configuration"""
    try:
        # Clean up any existing generated files
        if os.path.exists('generated_models'):
            shutil.rmtree('generated_models')
        if os.path.exists('generated_routes'):
            shutil.rmtree('generated_routes')
        if os.path.exists('templates/manifest'):
            shutil.rmtree('templates/manifest')
        
        # Create necessary directories
        os.makedirs('templates/generators', exist_ok=True)
        os.makedirs('generated_models', exist_ok=True)
        os.makedirs('generated_routes', exist_ok=True)
        
        # Use the manifest config as a test case
        generator = ModelGenerator({"manifest": model_registry["manifest"]})
        generator.generate_all()
        
        print("✓ Successfully generated files for manifest model")
        print("\nGenerated files:")
        print("- generated_models/manifest.py")
        print("- generated_routes/manifest_routes.py")
        print("- templates/manifest/list.html")
        print("- templates/manifest/form.html")
        
        # Read and print the generated model
        with open('generated_models/manifest.py', 'r') as f:
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
