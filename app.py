from flask import Flask, redirect, url_for
from flask_cors import CORS
from database import init_db, shutdown_session
from dotenv import load_dotenv
import os
from config import HOST, PORT

# Import generated route handlers
from generator.output.routes import register_manifest_routes

load_dotenv()

app = Flask(__name__, 
           static_folder='static', 
           static_url_path='/static',
           template_folder='generator/output/templates')
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

@app.teardown_appcontext
def shutdown_session_handler(exception=None):
    shutdown_session()

@app.route('/')
def index():
    return redirect(url_for('list_manifest'))

# Register generated routes
register_manifest_routes(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host=HOST, port=PORT)
