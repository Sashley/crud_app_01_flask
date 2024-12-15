from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response
from database import db_session
from generated_models.country import Country
from sqlalchemy import or_, cast, String, func
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('country', __name__, url_prefix='/country')

def register_country_routes(app):
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
    query = Country.query
    
    search = request.args.get('search', '').strip()
    logger.debug(f"Search parameter: '{search}'")
    
    if search:
        search_term = f"%{search}%"
        logger.debug(f"Search term: '{search_term}'")
        
        filters = [
            func.lower(Country.name).like(func.lower(search_term)),
            func.lower(Country.code).like(func.lower(search_term)),
            func.lower(Country.region).like(func.lower(search_term))
        ]
        
        query = query.filter(or_(*filters))
    
    sort = request.args.get('sort', '-id')
    logger.debug(f"Sort parameter: {sort}")
    
    is_desc = sort.startswith('-')
    sort_field = sort[1:] if is_desc else sort
    
    if hasattr(Country, sort_field):
        if is_desc:
            query = query.order_by(getattr(Country, sort_field).desc())
        else:
            query = query.order_by(getattr(Country, sort_field).asc())
    
    return query

@bp.route('/')
def list_country():
    logger.debug("Entering list_country route")
    try:
        # Get pagination parameters
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        
        # Get filtered query
        query = get_filtered_query()
        total_count = query.count()
        logger.debug(f"Total count: {total_count}")
        
        # Get paginated results
        items = query.offset(offset).limit(page_size).all()
        logger.debug(f"Found {len(items)} countries for page {page}")
        
        # Calculate if there are more pages
        has_more = total_count > (page * page_size)
        logger.debug(f"Has more pages: {has_more}")

        template_vars = {
            'items': items,
            'search': request.args.get('search', ''),
            'sort': request.args.get('sort', '-id'),
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': has_more,
            'entity_name': 'Country',
            'routes': {
                'list': 'country.list_country',
                'create': 'country.create_country',
                'edit': 'country.edit_country',
                'delete': 'country.delete_country'
            },
            'columns': [
                {
                    'key': 'code',
                    'label': 'Code',
                    'sortable': True,
                    'class': 'w-[100px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[100px]'
                },
                {
                    'key': 'name',
                    'label': 'Name',
                    'sortable': True,
                    'class': 'w-[200px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[200px]'
                },
                {
                    'key': 'region',
                    'label': 'Region',
                    'sortable': True,
                    'class': 'w-[160px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'responsive_class': 'hidden md:table-cell',
                    'width_class': 'max-w-[160px]'
                }
            ],
            'identifier_field': 'code'
        }
        
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        if is_htmx and page > 1:
            logger.debug("Returning rows template for HTMX request")
            return render_template('country/rows.html', **template_vars)
        elif is_htmx:
            logger.debug("Returning table template for HTMX request")
            return render_template('country/table.html', **template_vars)
        
        logger.debug("Returning full template")
        return render_template('country/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_country: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/new', methods=['GET', 'POST'])
def create_country():
    try:
        if request.method == 'POST':
            item = Country()
            item.name = request.form.get('name')
            item.code = request.form.get('code')
            item.region = request.form.get('region')
            
            db_session.add(item)
            db_session.commit()
            
            if request.headers.get('HX-Request'):
                response = make_response()
                response.headers['HX-Reswap'] = 'innerHTML'
                response.headers['HX-Retarget'] = '#modal-container'
                response.headers['HX-Trigger'] = 'modalClosed countrySaved'
                return response
            return redirect(url_for('country.list_country'))
        
        if request.headers.get('HX-Request'):
            return render_template('country/form_modal.html')
        return render_template('country/form.html')
    except Exception as e:
        logger.error(f"Error in create_country: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_country(id):
    try:
        item = Country.query.get(id)
        if item is None:
            abort(404)
        
        if request.method == 'POST':
            item.name = request.form.get('name')
            item.code = request.form.get('code')
            item.region = request.form.get('region')
            
            db_session.commit()
            
            if request.headers.get('HX-Request'):
                response = make_response()
                response.headers['HX-Reswap'] = 'innerHTML'
                response.headers['HX-Retarget'] = '#modal-container'
                response.headers['HX-Trigger'] = 'modalClosed countrySaved'
                return response
            return redirect(url_for('country.list_country'))
        
        if request.headers.get('HX-Request'):
            return render_template('country/form_modal.html', item=item)
        return render_template('country/form.html', item=item)
    except Exception as e:
        logger.error(f"Error in edit_country: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['POST', 'DELETE'])
def delete_country(id):
    try:
        item = Country.query.get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        
        if request.headers.get('HX-Request'):
            return ''
        return redirect(url_for('country.list_country'))
    except Exception as e:
        logger.error(f"Error in delete_country: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
