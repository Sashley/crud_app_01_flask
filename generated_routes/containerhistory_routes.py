from flask import Blueprint, render_template, request, jsonify, make_response
from database import db_session
from generated_models.containerhistory import ContainerHistory
from generated_models.container import Container
from generated_models.containerstatus import ContainerStatus
from generated_models.port import Port
from sqlalchemy import desc, or_
from datetime import datetime

bp = Blueprint('containerhistory', __name__, url_prefix='/containerhistory')

# Define columns at module level
columns = [
    {
        'key': 'container_id',
        'label': 'Container',
        'sortable': True,
        'width_class': 'max-w-[150px] sm:max-w-[170px]'
    },
    {
        'key': 'container_status_id',
        'label': 'Status',
        'sortable': True,
        'width_class': 'max-w-[150px] sm:max-w-[170px]'
    },
    {
        'key': 'port_id',
        'label': 'Port',
        'sortable': True,
        'width_class': 'max-w-[150px] sm:max-w-[170px]',
        'responsive_class': 'hidden md:table-cell'
    },
    {
        'key': 'damage',
        'label': 'Damage',
        'sortable': True,
        'width_class': 'max-w-[150px] sm:max-w-[170px]',
        'responsive_class': 'hidden lg:table-cell'
    },
    {
        'key': 'updated',
        'label': 'Timestamp',
        'sortable': True,
        'width_class': 'max-w-[150px] sm:max-w-[170px]',
        'responsive_class': 'hidden lg:table-cell'
    }
]

def register_containerhistory_routes(app):
    app.register_blueprint(bp)

@bp.route('/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response()
    # Add out-of-band swap to clear modal container
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

def get_filtered_query():
    query = ContainerHistory.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(ContainerHistory.damage.ilike(f'%{search}%'))
        query = query.filter(or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-updated')
    if sort.startswith('-'):
        sort_field = sort[1:]
        query = query.order_by(desc(getattr(ContainerHistory, sort_field)))
    else:
        query = query.order_by(getattr(ContainerHistory, sort_field))
    
    return query

@bp.route('/')
def list_containerhistory():
    page_size = int(request.args.get('page_size', '10'))
    page = int(request.args.get('page', '1'))
    offset = (page - 1) * page_size
    
    query = get_filtered_query()
    total_count = query.count()
    
    items = query.offset(offset).limit(page_size).all()
    
    template_vars = {
        'entity_name': 'containerhistory',
        'items': items,
        'search': request.args.get('search', ''),
        'sort': request.args.get('sort', '-updated'),
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'has_more': total_count > (page * page_size),
        'routes': {'list': 'containerhistory.list_containerhistory'},
        'columns': columns
    }
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    if is_htmx and page > 1:
        return render_template('containerhistory/rows.html', **template_vars)
    elif is_htmx:
        return render_template('containerhistory/table.html', **template_vars)
    
    return render_template('containerhistory/list.html', **template_vars)

@bp.route('/load-form', endpoint='load_form')
def load_form():
    history_id = request.args.get('id')
    history = None
    if history_id:
        history = ContainerHistory.query.get_or_404(history_id)
    
    containers = Container.query.all()
    statuses = ContainerStatus.query.all()
    ports = Port.query.all()
    
    return render_template(
        'containerhistory/form_modal.html',
        history=history,
        containers=containers,
        statuses=statuses,
        ports=ports
    )

@bp.route('/save', methods=['POST'])
def save():
    history_id = request.args.get('id') or request.form.get('id')
    
    if history_id:
        history = ContainerHistory.query.get_or_404(history_id)
    else:
        history = ContainerHistory()
        db_session.add(history)
    
    history.container_id = request.form.get('container_id')
    history.container_status_id = request.form.get('container_status_id')
    history.port_id = request.form.get('port_id')
    history.damage = request.form.get('damage')
    history.updated = datetime.now()
    
    db_session.commit()
    
    response = make_response()
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed containerhistorySaved'
    return response

@bp.route('/close_modal')
def close_modal():
    response = make_response()
    response.headers['HX-Reswap'] = 'innerHTML'
    response.headers['HX-Retarget'] = '#modal-container'
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

@bp.route('/<int:id>/delete', methods=['DELETE'])
def delete(id):
    history = ContainerHistory.query.get_or_404(id)
    db_session.delete(history)
    db_session.commit()
    
    query = get_filtered_query()
    page_size = int(request.args.get('page_size', '10'))
    items = query.limit(page_size).all()
    
    return render_template(
        'containerhistory/table.html',
        entity_name='containerhistory',
        items=items,
        routes={'list': 'containerhistory.list_containerhistory'},
        columns=columns,
        page=1,
        page_size=page_size,
        total_count=query.count()
    )
