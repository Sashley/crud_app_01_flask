from flask import Flask, redirect, url_for, render_template
from flask_cors import CORS
from database import init_db, shutdown_session, db_session
from dotenv import load_dotenv
import os
from config import HOST, PORT
from jinja2 import ChoiceLoader, FileSystemLoader
from generate_relationship_tree import register_routes
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import all generated route handlers
from generated_routes import (
    manifest_routes, lineitem_routes, commodity_routes,
    packtype_routes, container_routes, containerhistory_routes,
    containerstatus_routes, shippingcompany_routes, vessel_routes,
    voyage_routes, leg_routes, port_routes, portpair_routes,
    country_routes, client_routes, user_routes, rate_routes
)

# Import custom routes
from routes.vessel_ops import vessel_ops

load_dotenv()

app = Flask(__name__, 
           static_folder='static', 
           static_url_path='/static')

# Configure multiple template folders
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.root_path, 'templates')),
    FileSystemLoader(os.path.join(app.root_path, 'generator/output/templates'))
])

CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

@app.teardown_appcontext
def shutdown_session_handler(exception=None):
    logger.debug("Shutting down database session")
    shutdown_session()

@app.before_request
def before_request():
    logger.debug("Creating new database session")
    # Ensure we have a fresh session
    db_session.remove()

@app.route('/')
def index():
    return redirect(url_for('manifest.list_manifest'))

@app.route('/model-tree')
def model_tree():
    return render_template('model_tree.html')

# Register all generated routes
manifest_routes.register_manifest_routes(app)
lineitem_routes.register_lineitem_routes(app)
commodity_routes.register_commodity_routes(app)
packtype_routes.register_packtype_routes(app)
container_routes.register_container_routes(app)
containerhistory_routes.register_containerhistory_routes(app)
containerstatus_routes.register_containerstatus_routes(app)
shippingcompany_routes.register_shippingcompany_routes(app)
vessel_routes.register_vessel_routes(app)
voyage_routes.register_voyage_routes(app)
leg_routes.register_leg_routes(app)
port_routes.register_port_routes(app)
portpair_routes.register_portpair_routes(app)
country_routes.register_country_routes(app)
client_routes.register_client_routes(app)
user_routes.register_user_routes(app)
rate_routes.register_rate_routes(app)

# Register custom blueprints
app.register_blueprint(vessel_ops)

# Register relationship tree routes
register_routes(app)

if __name__ == '__main__':
    logger.info("Initializing database")
    init_db()
    logger.info(f"Starting Flask app on {HOST}:{PORT}")
    app.run(debug=True, host=HOST, port=PORT)
