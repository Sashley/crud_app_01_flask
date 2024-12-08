from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify
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

def get_form_choices():
    """Get all the choices needed for the lineitem form dropdowns"""
    manifests = db_session.query(Manifest).order_by(Manifest.bill_of_lading).all()
    pack_types = db_session.query(PackType).order_by(PackType.name).all()
    commodities = db_session.query(Commodity).order_by(Commodity.name).all()
    containers = db_session.query(Container).order_by(Container.number).all()
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
    # Start with a query that joins all related entities
    query = db_session.query(LineItem)\
        .outerjoin(Manifest, LineItem.manifest_id == Manifest.id)\
        .outerjoin(PackType, LineItem.pack_type_id == PackType.id)\
        .outerjoin(Commodity, LineItem.commodity_id == Commodity.id)\
        .outerjoin(Container, LineItem.container_id == Container.id)
    
    # Filter by manifest_id if provided
    manifest_id = request.args.get('manifest_id')
    logger.debug(f"Filtering by manifest_id: {manifest_id}")
    if manifest_id:
        query = query.filter(LineItem.manifest_id == manifest_id)
        # Debug: Check if any line items exist for this manifest
        count = query.count()
        logger.debug(f"Found {count} line items for manifest_id {manifest_id}")
        # Debug: Print first few line items
        items = query.limit(3).all()
        for item in items:
            logger.debug(f"Line item: id={item.id}, description={item.description}")
    
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
                func.lower(Container.number).like(func.lower(search_term))
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
    
    # Add columns to select
    query = query.add_columns(
        Manifest.bill_of_lading.label('manifest_bol'),
        PackType.name.label('pack_type_name'),
        Commodity.name.label('commodity_name'),
        Container.number.label('container_number')
    )
    
    return query

@bp.route('/')
def list_lineitem():
    logger.debug("Entering list_lineitem route")
    logger.debug(f"Request path: {request.path}")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request args: {request.args}")
    logger.debug(f"Request headers: {request.headers}")
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
        logger.debug(f"Found {len(results)} lineitems for page {page}")
        
        # Process results
        items = []
        for result in results:
            lineitem = result[0]
            lineitem.manifest_bol = result.manifest_bol
            lineitem.pack_type_name = result.pack_type_name
            lineitem.commodity_name = result.commodity_name
            lineitem.container_number = result.container_number
            items.append(lineitem)

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
            'manifest': manifest,  # Pass the manifest object
            'manifest_number': manifest_number,
            'routes': {
                'list': 'lineitem.list_lineitem',
                'create': 'lineitem.create_lineitem',
                'edit': 'lineitem.edit_lineitem',
                'delete': 'lineitem.delete_lineitem'
            },
            'columns': [
                {
                    'key': 'description',
                    'label': 'Description',
                    'sortable': True,
                    'class': 'w-[160px] sm:w-[180px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                },
                {
                    'key': 'quantity',
                    'label': 'Quantity',
                    'sortable': True,
                    'class': 'w-[100px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden sm:table-cell',
                    'width_class': 'max-w-[90px]'
                },
                {
                    'key': 'weight',
                    'label': 'Weight',
                    'sortable': True,
                    'class': 'w-[100px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden md:table-cell',
                    'width_class': 'max-w-[90px]'
                },
                {
                    'key': 'volume',
                    'label': 'Volume',
                    'sortable': True,
                    'class': 'w-[100px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden lg:table-cell',
                    'width_class': 'max-w-[90px]'
                },
                {
                    'key': 'pack_type_name',
                    'label': 'Pack Type',
                    'sortable': False,
                    'class': 'w-[120px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden xl:table-cell',
                    'width_class': 'max-w-[110px]'
                },
                {
                    'key': 'commodity_name',
                    'label': 'Commodity',
                    'sortable': False,
                    'class': 'w-[120px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden xl:table-cell',
                    'width_class': 'max-w-[110px]'
                },
                {
                    'key': 'container_number',
                    'label': 'Container',
                    'sortable': False,
                    'class': 'w-[120px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden xl:table-cell',
                    'width_class': 'max-w-[110px]'
                }
            ],
            'identifier_field': 'description'
        }
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        # If manifest_id is provided, return partial template
        if manifest_id:
            logger.debug("Returning partial list template")
            return render_template('lineitem/partial_list.html', **template_vars)
        
        # If this is an HTMX request for more items, return just the rows
        if is_htmx and page > 1:
            logger.debug("Returning rows template for HTMX request")
            return render_template('lineitem/rows.html', **template_vars)
        elif is_htmx:
            # For other HTMX requests (like search), return the full table
            logger.debug("Returning table template for HTMX request")
            return render_template('lineitem/table.html', **template_vars)
        
        # Otherwise return the full page
        logger.debug("Returning full template")
        return render_template('lineitem/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_lineitem: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/new', methods=['GET', 'POST'])
def create_lineitem():
    if request.method == 'POST':
        try:
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
            
            db_session.add(item)
            db_session.commit()
            
            # If manifest_id was provided in query params, redirect back to manifest list
            manifest_id = request.args.get('manifest_id')
            if manifest_id:
                return redirect(url_for('manifest.list_manifest'))
            return redirect(url_for('lineitem.list_lineitem'))
        except Exception as e:
            logger.error(f"Error in create_lineitem: {str(e)}", exc_info=True)
            db_session.rollback()
            raise
    
    # Pre-select manifest if manifest_id is provided
    manifest_id = request.args.get('manifest_id')
    if manifest_id:
        manifest = db_session.query(Manifest).get(manifest_id)
        if manifest is None:
            abort(404)
        item = LineItem(manifest_id=manifest_id)
    else:
        item = None
    
    choices = get_form_choices()
    return render_template('lineitem/form.html', item=item, **choices)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_lineitem(id):
    try:
        item = db_session.query(LineItem).get(id)
        if item is None:
            abort(404)
        
        if request.method == 'POST':
            item.manifest_id = request.form.get('manifest_id')
            item.description = request.form.get('description')
            item.quantity = request.form.get('quantity')
            item.weight = request.form.get('weight')
            item.volume = request.form.get('volume')
            item.pack_type_id = request.form.get('pack_type_id')
            item.commodity_id = request.form.get('commodity_id')
            item.container_id = request.form.get('container_id')
            item.manifester_id = request.form.get('manifester_id')
            
            db_session.commit()
            return redirect(url_for('manifest.list_manifest'))
        
        choices = get_form_choices()
        return render_template('lineitem/form.html', item=item, **choices)
    except Exception as e:
        logger.error(f"Error in edit_lineitem: {str(e)}", exc_info=True)
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
