from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, make_response
from database import db_session
from sqlalchemy import or_, cast, String, func
from sqlalchemy.orm import aliased
from generated_models.lineitem import LineItem
from generated_models.manifest import Manifest
from generated_models.packtype import PackType
from generated_models.commodity import Commodity
from generated_models.container import Container
from generated_models.user import User
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('lineitem', __name__, url_prefix='/lineitem')

def register_lineitem_routes(app):
    app.register_blueprint(bp)

@bp.route('/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response('')
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

def get_form_choices():
    """Get all the choices needed for the lineitem form dropdowns"""
    manifests = db_session.query(Manifest).order_by(Manifest.bill_of_lading).all()
    pack_types = db_session.query(PackType).order_by(PackType.name).all()
    commodities = db_session.query(Commodity).order_by(Commodity.name).all()
    containers = db_session.query(Container).order_by(Container.container_number).all()
    manifesters = db_session.query(User).order_by(User.name).all()
    
    return {
        'manifests': manifests,
        'pack_types': pack_types,
        'commodities': commodities,
        'containers': containers,
        'manifesters': manifesters
    }

def get_filtered_query():
    """Get base query with all joins and filters applied"""
    # Start with a query that joins all related entities and selects their names
    query = db_session.query(
        LineItem,
        PackType.name.label('pack_type_name'),
        Commodity.name.label('commodity_name'),
        Container.container_number.label('container_number'),
        Manifest.bill_of_lading.label('bol_number')  # Add BoL number to query
    ).outerjoin(Manifest, LineItem.manifest_id == Manifest.id)\
     .outerjoin(PackType, LineItem.pack_type_id == PackType.id)\
     .outerjoin(Commodity, LineItem.commodity_id == Commodity.id)\
     .outerjoin(Container, LineItem.container_id == Container.id)
    
    # Filter by manifest_id if provided
    manifest_id = request.args.get('manifest_id')
    logger.debug(f"Filtering by manifest_id: {manifest_id}")
    if manifest_id:
        query = query.filter(LineItem.manifest_id == manifest_id)
    
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
                cast(LineItem.id, String).ilike(search_term),
                cast(LineItem.quantity, String).ilike(search_term),
                cast(LineItem.weight, String).ilike(search_term),
                cast(LineItem.volume, String).ilike(search_term),
                # Search in manifest's bill of lading
                func.lower(Manifest.bill_of_lading).like(func.lower(search_term))
            ]
        else:
            logger.debug("Search term is text")
            filters = [
                func.lower(LineItem.description).like(func.lower(search_term)),
                # Search in related entities
                func.lower(Manifest.bill_of_lading).like(func.lower(search_term)),
                func.lower(PackType.name).like(func.lower(search_term)),
                func.lower(Commodity.name).like(func.lower(search_term)),
                func.lower(Container.container_number).like(func.lower(search_term))
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
        query = query.order_by(getattr(LineItem, sort_field).desc())
    else:
        query = query.order_by(getattr(LineItem, sort))
    
    return query

@bp.route('/')
def list_lineitem():
    logger.debug("Entering list_lineitem route")
    try:
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        
        query = get_filtered_query()
        
        # Get total count for pagination
        total_count = query.count()
        logger.debug(f"Total count: {total_count}")
        
        # Apply pagination
        results = query.offset(offset).limit(page_size).all()
        # Convert results to dictionaries with all fields
        items = []
        for result in results:
            item_dict = result[0].__dict__
            item_dict['pack_type_name'] = result[1]
            item_dict['commodity_name'] = result[2]
            item_dict['container_number'] = result[3]
            item_dict['bol_number'] = result[4]  # Add BoL number to item dictionary
            items.append(item_dict)
        logger.debug(f"Found {len(items)} lineitems for page {page}")

        # Get manifest if manifest_id is provided
        manifest_id = request.args.get('manifest_id')
        manifest = None
        manifest_number = None
        if manifest_id:
            logger.debug(f"Looking up manifest with ID: {manifest_id}")
            manifest = db_session.query(Manifest).get(manifest_id)
            if manifest is None:
                logger.error(f"Manifest not found with ID: {manifest_id}")
                abort(404)
            manifest_number = manifest.bill_of_lading
            logger.debug(f"Found manifest: {manifest_number}")

        # Common template variables
        template_vars = {
            'items': items,
            'search': request.args.get('search', ''),
            'sort': request.args.get('sort', '-id'),
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': total_count > (page * page_size),
            'entity_name': 'LineItem',
            'manifest': manifest,
            'manifest_number': manifest_number,
            'routes': {
                'list': 'lineitem.list_lineitem',
                'create': 'lineitem.load_form',
                'edit': 'lineitem.load_form',
                'delete': 'lineitem.delete_lineitem'
            },
            'columns': [
                {
                    'key': 'description',
                    'label': 'Description',
                    'sortable': False,
                    'class': 'px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': '', #sm:w-[30%]
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'pack_type_name',
                    'label': 'Pack Type',
                    'sortable': False,
                    'class': 'px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden sm:table-cell',
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'commodity_name',
                    'label': 'Commodity',
                    'sortable': False,
                    'class': 'w-[15%] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden md:table-cell',
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'container_number',
                    'label': 'Container',
                    'sortable': False,
                    'class': 'w-[15%] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden md:table-cell',
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'quantity',
                    'label': 'Quantity',
                    'sortable': True,
                    'class': 'w-[8%] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden lg:table-cell',
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'weight',
                    'label': 'Weight',
                    'sortable': True,
                    'class': 'w-[8%] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden xl:table-cell',
                    'width_class': 'max-w-full'
                },
                {
                    'key': 'volume',
                    'label': 'Volume',
                    'sortable': True,
                    'class': 'w-[8%] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    'responsive_class': 'hidden xl:table-cell',
                    'width_class': 'max-w-full'
                }
            ],
            'identifier_field': 'bol_number'  # Changed to use BoL number as identifier
        }
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        # If manifest_id is provided and this is a table refresh, return just the table
        if manifest_id and is_htmx and request.headers.get('HX-Target') == 'lineitem-table-container':
            logger.debug("Returning table template for HTMX refresh")
            return render_template('lineitem/table.html', **template_vars)
        
        # If manifest_id is provided, return partial template
        if manifest_id:
            logger.debug("Returning partial list template")
            return render_template('lineitem/partial_list.html', **template_vars)
        
        # Otherwise return the full page
        logger.debug("Returning full template")
        return render_template('lineitem/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_lineitem: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/load-form', methods=['GET'])
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        manifest_id = request.args.get('manifest_id')
        
        if id:
            item = db_session.query(LineItem).get(id)
            if item is None:
                abort(404)
        else:
            item = LineItem()
            if manifest_id:
                item.manifest_id = manifest_id
            
        choices = get_form_choices()
        return render_template('lineitem/form_modal.html', item=item, manifest_id=manifest_id, **choices)
    except Exception as e:
        logger.error(f"Error in load_form: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/save', methods=['POST'])
def save_lineitem():
    """Save lineitem via HTMX form submission"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(LineItem).get(id)
            if item is None:
                abort(404)
        else:
            item = LineItem()
            
        item.manifest_id = request.form.get('manifest_id')
        item.description = request.form.get('description')
        item.quantity = request.form.get('quantity')
        item.weight = request.form.get('weight')
        item.volume = request.form.get('volume')
        item.pack_type_id = request.form.get('pack_type_id')
        item.commodity_id = request.form.get('commodity_id')
        item.container_id = request.form.get('container_id')
        item.manifester_id = request.form.get('manifester_id')
        
        if not id:
            db_session.add(item)
        db_session.commit()
        
        # Create response with HX-Trigger header
        response = make_response('')
        response.headers['HX-Trigger'] = 'modalClosed lineitemSaved'
        return response
    except Exception as e:
        logger.error(f"Error in save_lineitem: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_lineitem(id):
    try:
        item = db_session.query(LineItem).get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('manifest.list_manifest'))
    except Exception as e:
        logger.error(f"Error in delete_lineitem: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
