from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response
from database import db_session
from sqlalchemy import or_, cast, String
from generated_models.user import User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('user', __name__, url_prefix='/user')

def register_user_routes(app):
    app.register_blueprint(bp)

@bp.route('/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response()
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

@bp.route('/')
def list_user():
    logger.debug("Entering list_user route")
    try:
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        
        query = db_session.query(User)
        
        search = request.args.get('search', '').strip()
        logger.debug(f"Search parameter: '{search}'")
        
        if search:
            search_term = f"%{search}%"
            logger.debug(f"Search term: '{search_term}'")
            
            filters = [
                cast(User.id, String).ilike(search_term),
                User.name.ilike(search_term),
                User.email.ilike(search_term)
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

        if hasattr(User, sort_field):
            if is_desc:
                query = query.order_by(getattr(User, sort_field).desc())
            else:
                query = query.order_by(getattr(User, sort_field).asc())
        
        total_count = query.count()
        logger.debug(f"Total count: {total_count}")
        
        items = query.offset(offset).limit(page_size).all()
        logger.debug(f"Found {len(items)} users for page {page}")

        template_vars = {
            'items': items,
            'search': request.args.get('search', ''),
            'sort': request.args.get('sort', '-id'),
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': total_count > (page * page_size),
            'entity_name': 'User',
            'routes': {
                'list': 'user.list_user',
                'create': 'user.create_user',
                'edit': 'user.edit_user',
                'delete': 'user.delete_user'
            },
            'columns': [
                {
                    'key': 'name',
                    'label': 'Name',
                    'sortable': True,
                    'class': 'w-[160px] sm:w-[180px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                },
                {
                    'key': 'email',
                    'label': 'Email',
                    'sortable': True,
                    'class': 'w-[160px] sm:w-[180px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                }
            ],
            'identifier_field': 'name'
        }
        
        is_htmx = request.headers.get('HX-Request') == 'true'
        logger.debug(f"Is HTMX request: {is_htmx}")
        
        if is_htmx and page > 1:
            logger.debug("Returning rows template for HTMX request")
            return render_template('user/rows.html', **template_vars)
        elif is_htmx:
            logger.debug("Returning table template for HTMX request")
            return render_template('user/table.html', **template_vars)
        
        logger.debug("Returning full template")
        return render_template('user/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_user: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/load-form', methods=['GET'])
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(User).get(id)
            if item is None:
                abort(404)
        else:
            item = None
            
        return render_template('user/form_modal.html', item=item)
    except Exception as e:
        logger.error(f"Error in load_form: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/save', methods=['POST'])
def save_user():
    """Save user via HTMX form submission"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(User).get(id)
            if item is None:
                abort(404)
        else:
            item = User()
            
        item.name = request.form.get('name')
        item.email = request.form.get('email')
        if request.form.get('password'):  # Only update password if provided
            item.password_hash = request.form.get('password')
        
        if not id:
            db_session.add(item)
        db_session.commit()
        
        # Create response with HX-Trigger header
        response = make_response()
        response.headers['HX-Reswap'] = 'innerHTML'
        response.headers['HX-Retarget'] = '#modal-container'
        response.headers['HX-Trigger'] = 'modalClosed userSaved'
        return response
    except Exception as e:
        logger.error(f"Error in save_user: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_user(id):
    try:
        item = db_session.query(User).get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('user.list_user'))
    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
