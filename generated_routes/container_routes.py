from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response
from database import db_session
from sqlalchemy import or_, cast, String, func
from generated_models.container import Container
from generated_models.containerstatus import ContainerStatus
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('container', __name__, url_prefix='/container')

def register_container_routes(app):
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
    """Get all the choices needed for the container form dropdowns"""
    statuses = db_session.query(ContainerStatus).order_by(ContainerStatus.name).all()
    return {'statuses': statuses}

def get_filtered_query():
    """Get base query with all joins and filters applied"""
    query = db_session.query(Container)\
        .outerjoin(ContainerStatus, Container.status_id == ContainerStatus.id)
    
    search = request.args.get('search', '').strip()
    if search:
        search_term = f"%{search}%"
        filters = [
            func.lower(Container.container_number).like(func.lower(search_term)),
            func.lower(Container.container_type).like(func.lower(search_term)),
            func.lower(Container.size).like(func.lower(search_term)),
            func.lower(ContainerStatus.name).like(func.lower(search_term))
        ]
        query = query.filter(or_(*filters))
    
    sort = request.args.get('sort', '-id')
    is_desc = sort.startswith('-')
    sort_field = sort[1:] if is_desc else sort

    if sort_field == 'status_name':
        if is_desc:
            query = query.order_by(ContainerStatus.name.desc())
        else:
            query = query.order_by(ContainerStatus.name.asc())
    elif hasattr(Container, sort_field):
        if is_desc:
            query = query.order_by(getattr(Container, sort_field).desc())
        else:
            query = query.order_by(getattr(Container, sort_field).asc())
    
    return query

@bp.route('/')
def list_container():
    try:
        page_size = int(request.args.get('page_size', '10'))
        page = int(request.args.get('page', '1'))
        offset = (page - 1) * page_size
        
        query = get_filtered_query()
        total_count = query.count()
        
        items = query.offset(offset).limit(page_size).all()

        template_vars = {
            'items': items,
            'search': request.args.get('search', ''),
            'sort': request.args.get('sort', '-id'),
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'has_more': total_count > (page * page_size),
            'entity_name': 'Container',
            'routes': {
                'list': 'container.list_container',
                'create': 'container.create_container',
                'edit': 'container.edit_container',
                'delete': 'container.delete_container'
            },
            'columns': [
                {
                    'key': 'container_number',
                    'label': 'Container Number',
                    'sortable': True,
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                },
                {
                    'key': 'container_type',
                    'label': 'Type',
                    'sortable': True,
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                },
                {
                    'key': 'size',
                    'label': 'Size',
                    'sortable': True,
                    'responsive_class': 'hidden md:table-cell',
                    'width_class': 'max-w-[150px] sm:max-w-[170px]'
                },
                {
                    'key': 'max_weight',
                    'label': 'Max Weight',
                    'sortable': True,
                    'responsive_class': 'hidden lg:table-cell',
                    'width_class': 'max-w-[130px] sm:max-w-[150px]'
                },
                {
                    'key': 'status_name',
                    'label': 'Status',
                    'sortable': True,
                    'responsive_class': 'hidden lg:table-cell',
                    'width_class': 'max-w-[130px] sm:max-w-[150px]'
                }
            ]
        }
        
        is_htmx = request.headers.get('HX-Request') == 'true'
        if is_htmx and page > 1:
            return render_template('container/rows.html', **template_vars)
        elif is_htmx:
            return render_template('container/table.html', **template_vars)
        
        return render_template('container/list.html', **template_vars)
    except Exception as e:
        logger.error(f"Error in list_container: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/load-form', methods=['GET'])
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(Container).get(id)
            if item is None:
                abort(404)
        else:
            item = None
            
        choices = get_form_choices()
        return render_template('container/form_modal.html', item=item, **choices)
    except Exception as e:
        logger.error(f"Error in load_form: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/save', methods=['POST'])
def save_container():
    """Save container via HTMX form submission"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(Container).get(id)
            if item is None:
                abort(404)
        else:
            item = Container()
            
        item.container_number = request.form.get('container_number')
        item.container_type = request.form.get('container_type')
        item.size = request.form.get('size')
        item.max_weight = request.form.get('max_weight')
        item.status_id = request.form.get('status_id')
        
        if not id:
            db_session.add(item)
        db_session.commit()
        
        response = make_response()
        response.headers['HX-Reswap'] = 'innerHTML'
        response.headers['HX-Retarget'] = '#modal-container'
        response.headers['HX-Trigger'] = 'modalClosed containerSaved'
        return response
    except Exception as e:
        logger.error(f"Error in save_container: {str(e)}", exc_info=True)
        db_session.rollback()
        raise

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_container(id):
    try:
        item = db_session.query(Container).get(id)
        if item is None:
            abort(404)
            
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('container.list_container'))
    except Exception as e:
        logger.error(f"Error in delete_container: {str(e)}", exc_info=True)
        db_session.rollback()
        raise
