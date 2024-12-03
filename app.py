from flask import Flask
from flask_cors import CORS
from database import init_db, shutdown_session
from dotenv import load_dotenv
import os
import config

# Import generated route handlers
from generated_routes.manifest_routes import register_manifest_routes

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

@app.teardown_appcontext
def shutdown_session_handler(exception=None):
    shutdown_session()

# Register generated routes
register_manifest_routes(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host=config.HOST, port=config.PORT)
