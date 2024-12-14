from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response
from database import db_session
from generated_models.vessel import Vessel
from generated_models.shippingcompany import ShippingCompany
from sqlalchemy import or_, func
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('vessel', __name__, url_prefix='/vessel')

def register_vessel_routes(app):
    app.register_blueprint(bp)

@bp.route('/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response()
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

def get_form_choices():
    """Get all the choices needed for the vessel form dropdowns"""
    shipping_companies = db_session.query(ShippingCompany).order_by(ShippingCompany.name).all()
    return {'shipping_companies': shipping_companies}

@bp.route('/')
def list_vessel():
    try:
        logger.debug("Entering list_vessel route")
        
        # Get pagination parameters
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        logger.debug(f"Pagination: page={page}, page_size={page_size}, offset={offset}")
        
        # Build base query with join
        query = db_session.query(Vessel).outerjoin(ShippingCompany)
        
        # Apply search filters
        search = request.args.get('search', '').strip()
        logger.debug(f"Search term: {search}")
        
        if search:
            search_term = f"%{search}%"
            filters = [
                Vessel.name.ilike(search_term),
                ShippingCompany.name.ilike(search_term)
            ]
            query = query.filter(or_(*filters))
        
        # Apply sorting
        sort = request.args.get('sort', '-id')
        logger.debug(f"Sort parameter: {sort}")
        
        is_desc = sort.startswith('-')
        if is_desc:
            sort_field = sort[1:]
        else:
            sort_field = sort

        if sort_field == 'shipping_company.name':
            if is_desc:
                query = query.order_by(ShippingCompany.name.desc())
            else:
                query = query.order_by(ShippingCompany.name.asc())
        elif hasattr(Vessel, sort_field):
            if is_desc:
                query = query.order_by(getattr(Vessel, sort_field).desc())
            else:
                query = query.order_by(getattr(Vessel, sort_field).asc())
        
        # Get total count before pagination
        total_count = query.count()
        logger.debug(f"Total count: {total_count}")
        
        # Apply pagination
        items = query.offset(offset).limit(page_size).all()
        logger.debug(f"Found {len(items)} vessels for current page")
        
        template_vars = {
            'items': items,
            'search': search,
            'sort': sort,
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': total_count > (page * page_size),
            'entity_name': 'Vessel',
            'routes': {
                'list': 'vessel.list_vessel',
                'create': 'vessel.load_form',
                'edit': 'vessel.load_form',
                'delete': 'vessel.delete_vessel'
            },
            'columns': [
                {
                    'key': 'name',
                    'label': 'Name',
                    'sortable': True,
                    'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                },
                {
                    'key': 'shipping_company.name',
                    'label': 'Shipping Company',
                    'sortable': True,
                    'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                }
            ]
        }
        
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        if is_htmx and page > 1:
            logger.debug("Returning rows template for HTMX request")
            return render_template('vessel/rows.html', **template_vars)
        elif is_htmx:
            logger.debug("Returning table template for HTMX request")
            return render_template('vessel/table.html', **template_vars)
        
        logger.debug("Returning full list template")
        return render_template('vessel/list.html', **template_vars)
        
    except Exception as e:
        logger.error(f"Error in list_vessel: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/load-form', methods=['GET'])
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        if id:
            vessel = db_session.query(Vessel).get(id)
            if vessel is None:
                abort(404)
        else:
            vessel = None
            
        choices = get_form_choices()
        return render_template('vessel/form_modal.html', vessel=vessel, **choices)
    except Exception as e:
        logger.error(f"Error in load_form: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/save', methods=['POST'])
def save_vessel():
    """Save vessel via HTMX form submission"""
    try:
        id = request.form.get('id')
        if id:
            vessel = db_session.query(Vessel).get(id)
            if vessel is None:
                abort(404)
        else:
            vessel = Vessel()
            
        vessel.name = request.form.get('name')
        vessel.shipping_company_id = request.form.get('shipping_company_id')
        
        if not id:
            db_session.add(vessel)
        db_session.commit()
        
        # Return empty response with trigger headers
        response = make_response()
        response.headers['HX-Trigger'] = 'vesselSaved'
        return empty()
    except Exception as e:
        logger.error(f"Error in save_vessel: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_vessel(id):
    try:
        vessel = db_session.query(Vessel).get(id)
        if vessel is None:
            abort(404)
            
        db_session.delete(vessel)
        db_session.commit()
        
        # Return updated table with pagination
        query = db_session.query(Vessel).outerjoin(ShippingCompany)
        page_size = int(request.args.get('page_size', '10'))
        items = query.limit(page_size).all()
        
        template_vars = {
            'items': items,
            'page': 1,
            'page_size': page_size,
            'total_count': query.count(),
            'entity_name': 'Vessel',
            'routes': {
                'list': 'vessel.list_vessel',
                'create': 'vessel.load_form',
                'edit': 'vessel.load_form',
                'delete': 'vessel.delete_vessel'
            },
            'columns': [
                {
                    'key': 'name',
                    'label': 'Name',
                    'sortable': True,
                    'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                },
                {
                    'key': 'shipping_company.name',
                    'label': 'Shipping Company',
                    'sortable': True,
                    'class': 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                }
            ]
        }
        
        return render_template('vessel/table.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in delete_vessel: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
