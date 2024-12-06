from flask import Flask, redirect, url_for
from flask_cors import CORS
from database import init_db, shutdown_session
from dotenv import load_dotenv
import os
from config import HOST, PORT

# Import all generated route handlers
from generator.output.routes import (
    register_manifest_routes, register_lineitem_routes, register_commodity_routes,
    register_packtype_routes, register_container_routes, register_containerhistory_routes,
    register_containerstatus_routes, register_shippingcompany_routes, register_vessel_routes,
    register_voyage_routes, register_leg_routes, register_port_routes, register_portpair_routes,
    register_country_routes, register_client_routes, register_user_routes, register_rate_routes
)

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

# Register all generated routes
register_manifest_routes(app)
register_lineitem_routes(app)
register_commodity_routes(app)
register_packtype_routes(app)
register_container_routes(app)
register_containerhistory_routes(app)
register_containerstatus_routes(app)
register_shippingcompany_routes(app)
register_vessel_routes(app)
register_voyage_routes(app)
register_leg_routes(app)
register_port_routes(app)
register_portpair_routes(app)
register_country_routes(app)
register_client_routes(app)
register_user_routes(app)
register_rate_routes(app)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host=HOST, port=PORT)
