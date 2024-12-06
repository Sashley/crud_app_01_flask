from flask import Blueprint, render_template, request, redirect, url_for, abort
from database import db_session
from sqlalchemy import or_, cast, String, func
from sqlalchemy.orm import aliased
from generated_models.manifest import Manifest
from generated_models.client import Client
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.port import Port
from generated_models.user import User
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('manifest', __name__)

def register_manifest_routes(app):
    app.register_blueprint(bp)

def get_form_choices():
    """Get all the choices needed for the manifest form dropdowns"""
    clients = db_session.query(Client).order_by(Client.name).all()
    vessels = db_session.query(Vessel).order_by(Vessel.name).all()
    voyages = db_session.query(Voyage).order_by(Voyage.name).all()
    ports = db_session.query(Port).order_by(Port.name).all()
    manifesters = db_session.query(User).order_by(User.name).all()
    
    return {
        'clients': clients,
        'vessels': vessels,
        'voyages': voyages,
        'ports': ports,
        'manifesters': manifesters
    }

def parse_date(date_str):
    """Convert date string to datetime object if not None"""
    if date_str:
        try:
            logger.debug(f"Parsing date string: {date_str}")
            # Add time component to make it a full datetime
            date_with_time = f"{date_str} 00:00:00"
            parsed_date = datetime.strptime(date_with_time, '%Y-%m-%d %H:%M:%S')
            logger.debug(f"Parsed date: {parsed_date}")
            return parsed_date
        except ValueError as e:
            logger.error(f"Error parsing date: {e}")
            return None
    logger.debug("No date string provided")
    return None

@bp.route('/manifest')
def list_manifest():
    logger.debug("Entering list_manifest route")
    try:
        # Create aliases for the same table used multiple times
        ShipperAlias = aliased(Client)
        ConsigneeAlias = aliased(Client)
        
        # Start with a query that joins all related entities
        query = db_session.query(Manifest)\
            .outerjoin(ShipperAlias, Manifest.shipper_id == ShipperAlias.id)\
            .outerjoin(ConsigneeAlias, Manifest.consignee_id == ConsigneeAlias.id)\
            .outerjoin(Vessel, Manifest.vessel_id == Vessel.id)\
            .outerjoin(Voyage, Manifest.voyage_id == Voyage.id)
        
        # Apply search filters
        search = request.args.get('search', '').strip()
        logger.debug(f"Search parameter: '{search}'")
        
        if search:
            search_term = f"%{search}%"
            logger.debug(f"Search term: '{search_term}'")
            
            # Convert IDs to string for comparison if the search term looks like a number
            if search.isdigit():
                logger.debug("Search term is numeric")
                filters = [
                    cast(Manifest.id, String).ilike(search_term),
                    cast(Manifest.shipper_id, String).ilike(search_term),
                    cast(Manifest.consignee_id, String).ilike(search_term),
                    cast(Manifest.vessel_id, String).ilike(search_term),
                    cast(Manifest.voyage_id, String).ilike(search_term),
                    # Also search in bill of lading for numeric patterns
                    func.lower(Manifest.bill_of_lading).like(func.lower(search_term))
                ]
            else:
                logger.debug("Search term is text")
                filters = [
                    # Case-insensitive search for bill of lading
                    func.lower(Manifest.bill_of_lading).like(func.lower(search_term)),
                    func.lower(Manifest.place_of_delivery).like(func.lower(search_term)),
                    func.lower(Manifest.place_of_receipt).like(func.lower(search_term)),
                    # Search in related entities
                    func.lower(ShipperAlias.name).like(func.lower(search_term)),
                    func.lower(ConsigneeAlias.name).like(func.lower(search_term)),
                    func.lower(Vessel.name).like(func.lower(search_term)),
                    func.lower(Voyage.name).like(func.lower(search_term))
                ]
            
            # Remove None filters
            filters = [f for f in filters if f is not None]
            
            if filters:
                query = query.filter(or_(*filters))
                logger.debug(f"Applied {len(filters)} search filters")
        
        # Apply sorting
        sort = request.args.get('sort', '-id')
        logger.debug(f"Sort parameter: {sort}")
        
        if sort.startswith('-'):
            sort_field = sort[1:]
            query = query.order_by(getattr(Manifest, sort_field).desc())
        else:
            query = query.order_by(getattr(Manifest, sort))
        
        # Add columns to select
        query = query.add_columns(
            ShipperAlias.name.label('shipper_name'),
            ConsigneeAlias.name.label('consignee_name'),
            Vessel.name.label('vessel_name'),
            Voyage.name.label('voyage_name')
        )
        
        # Execute query
        results = query.all()
        logger.debug(f"Found {len(results)} manifests")
        
        # Process results
        items = []
        for result in results:
            manifest = result[0]
            manifest.shipper_name = result.shipper_name
            manifest.consignee_name = result.consignee_name
            manifest.vessel_name = result.vessel_name
            manifest.voyage_name = result.voyage_name
            items.append(manifest)
        
        # Log first few results for debugging
        for item in items[:3]:
            logger.debug(f"Sample manifest: ID={item.id}, BL={item.bill_of_lading}, "
                        f"Shipper={item.shipper_name}, Consignee={item.consignee_name}, "
                        f"Vessel={item.vessel_name}, Voyage={item.voyage_name}")
        
        return render_template(
            'manifest/list.html',
            items=items,
            search=search,
            sort=sort
        )
    except Exception as e:
        logger.error(f"Error in list_manifest: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/manifest/new', methods=['GET', 'POST'])
def create_manifest():
    if request.method == 'POST':
        try:
            item = Manifest()
            item.bill_of_lading = request.form.get('bill_of_lading')
            item.shipper_id = request.form.get('shipper_id')
            item.consignee_id = request.form.get('consignee_id')
            item.vessel_id = request.form.get('vessel_id')
            item.voyage_id = request.form.get('voyage_id')
            item.port_of_loading_id = request.form.get('port_of_loading_id')
            item.port_of_discharge_id = request.form.get('port_of_discharge_id')
            item.place_of_delivery = request.form.get('place_of_delivery')
            item.place_of_receipt = request.form.get('place_of_receipt')
            item.clauses = request.form.get('clauses')
            
            date_str = request.form.get('date_of_receipt')
            logger.debug(f"Create - Received date string: {date_str}")
            item.date_of_receipt = parse_date(date_str)
            logger.debug(f"Create - Parsed date: {item.date_of_receipt}")
            
            item.manifester_id = request.form.get('manifester_id')
            
            db_session.add(item)
            db_session.commit()
            return redirect(url_for('manifest.list_manifest'))
        except Exception as e:
            logger.error(f"Error in create_manifest: {str(e)}", exc_info=True)
            db_session.rollback()
            raise
    
    choices = get_form_choices()
    return render_template('manifest/form.html', **choices)

@bp.route('/manifest/<int:id>/edit', methods=['GET', 'POST'])
def edit_manifest(id):
    try:
        item = db_session.query(Manifest).get(id)
        if item is None:
            abort(404)
        
        if request.method == 'POST':
            item.bill_of_lading = request.form.get('bill_of_lading')
            item.shipper_id = request.form.get('shipper_id')
            item.consignee_id = request.form.get('consignee_id')
            item.vessel_id = request.form.get('vessel_id')
            item.voyage_id = request.form.get('voyage_id')
            item.port_of_loading_id = request.form.get('port_of_loading_id')
            item.port_of_discharge_id = request.form.get('port_of_discharge_id')
            item.place_of_delivery = request.form.get('place_of_delivery')
            item.place_of_receipt = request.form.get('place_of_receipt')
            item.clauses = request.form.get('clauses')
            
            date_str = request.form.get('date_of_receipt')
            logger.debug(f"Edit - Received date string: {date_str}")
            item.date_of_receipt = parse_date(date_str)
            logger.debug(f"Edit - Parsed date: {item.date_of_receipt}")
            
            item.manifester_id = request.form.get('manifester_id')
            
            db_session.commit()
            return redirect(url_for('manifest.list_manifest'))
        
        # Format the date for display in the form
        if item.date_of_receipt:
            item.date_of_receipt = item.date_of_receipt.strftime('%Y-%m-%d')
        
        choices = get_form_choices()
        return render_template('manifest/form.html', item=item, **choices)
    except Exception as e:
        logger.error(f"Error in edit_manifest: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/manifest/<int:id>/delete', methods=['POST'])
def delete_manifest(id):
    try:
        item = db_session.query(Manifest).get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('manifest.list_manifest'))
    except Exception as e:
        logger.error(f"Error in delete_manifest: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
