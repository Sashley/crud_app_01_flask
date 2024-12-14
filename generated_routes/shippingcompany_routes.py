from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response
from database import db_session
from sqlalchemy import or_, cast, String, func
from generated_models.shippingcompany import ShippingCompany
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('shippingcompany', __name__, url_prefix='/shippingcompany')

def register_shippingcompany_routes(app):
    app.register_blueprint(bp)

@bp.route('/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response()
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

def get_filtered_query():
    """Get base query with all filters applied"""
    query = db_session.query(ShippingCompany)
    
    search = request.args.get('search', '').strip()
    logger.debug(f"Search parameter: '{search}'")
    
    if search:
        search_term = f"%{search}%"
        logger.debug(f"Search term: '{search_term}'")
        
        if search.isdigit():
            logger.debug("Search term is numeric")
            filters = [
                cast(ShippingCompany.id, String).ilike(search_term)
            ]
        else:
            logger.debug("Search term is text")
            filters = [
                func.lower(ShippingCompany.name).like(func.lower(search_term))
            ]
        
        filters = [f for f in filters if f is not None]
        
        if filters:
            query = query.filter(or_(*filters))
            logger.debug(f"Applied {len(filters)} search filters")
    
    sort = request.args.get('sort', '-id')
    logger.debug(f"Sort parameter: {sort}")
    
    is_desc = sort.startswith('-')
    if is_desc:
        sort_field = sort[1:]
    else:
        sort_field = sort

    if hasattr(ShippingCompany, sort_field):
        if is_desc:
            query = query.order_by(getattr(ShippingCompany, sort_field).desc())
        else:
            query = query.order_by(getattr(ShippingCompany, sort_field).asc())
    
    return query

@bp.route('/')
def list_shippingcompany():
    logger.debug("Entering list_shippingcompany route")
    try:
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        
        query = get_filtered_query()
        total_count = query.count()
        logger.debug(f"Total count: {total_count}")
        
        items = query.offset(offset).limit(page_size).all()
        logger.debug(f"Found {len(items)} shipping companies for page {page}")

        template_vars = {
            'items': items,
            'search': request.args.get('search', ''),
            'sort': request.args.get('sort', '-id'),
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': total_count > (page * page_size),
            'entity_name': 'shippingcompany',  # Changed to single word for HTML IDs
            'entity_title': 'Shipping Company',  # Added for display purposes
            'routes': {
                'list': 'shippingcompany.list_shippingcompany',
                'create': 'shippingcompany.create_shippingcompany',
                'edit': 'shippingcompany.edit_shippingcompany',
                'delete': 'shippingcompany.delete_shippingcompany'
            },
            'columns': [
                {
                    'key': 'name',
                    'label': 'Company Name',
                    'sortable': True,
                    'class': 'w-[200px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[200px] sm:max-w-[300px]'
                }
            ],
            'identifier_field': 'name'
        }
        
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        if is_htmx and page > 1:
            logger.debug("Returning rows template for HTMX request")
            return render_template('shippingcompany/rows.html', **template_vars)
        elif is_htmx:
            logger.debug("Returning table template for HTMX request")
            return render_template('shippingcompany/table.html', **template_vars)
        
        logger.debug("Returning full template")
        return render_template('shippingcompany/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_shippingcompany: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/load-form', methods=['GET'])
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(ShippingCompany).get(id)
            if item is None:
                abort(404)
        else:
            item = None
            
        return render_template('shippingcompany/form_content.html', item=item)
    except Exception as e:
        logger.error(f"Error in load_form: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/save', methods=['POST'])
def save_shippingcompany():
    """Save shipping company via HTMX form submission"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(ShippingCompany).get(id)
            if item is None:
                abort(404)
        else:
            item = ShippingCompany()
            
        item.name = request.form.get('name')
        
        if not id:
            db_session.add(item)
        db_session.commit()
        
        # Create response with HX-Trigger header
        response = make_response()
        response.headers['HX-Reswap'] = 'innerHTML'
        response.headers['HX-Retarget'] = '#modal-container'
        response.headers['HX-Trigger'] = 'modalClosed shippingcompanySaved'
        return response
    except Exception as e:
        logger.error(f"Error in save_shippingcompany: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_shippingcompany(id):
    try:
        item = db_session.query(ShippingCompany).get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('shippingcompany.list_shippingcompany'))
    except Exception as e:
        logger.error(f"Error in delete_shippingcompany: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
