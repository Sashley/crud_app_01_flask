from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database import db_session
from sqlalchemy import or_
from generated_models.containerstatus import ContainerStatus

bp = Blueprint('containerstatus', __name__)

class Routes:
    def __init__(self, bp):
        self.list = f"{bp.name}.list_containerstatus"
        self.create_form = f"{bp.name}.create_form"
        self.edit_form = f"{bp.name}.edit_form"
        self.delete = f"{bp.name}.delete_containerstatus"
        self.create_containerstatus = f"{bp.name}.create_containerstatus"
        self.edit_containerstatus = f"{bp.name}.edit_containerstatus"

def register_containerstatus_routes(app):
    app.register_blueprint(bp)

@bp.route('/containerstatus')
def list_containerstatus():
    query = ContainerStatus.query
    
    # Apply search filters
    search = request.args.get('search', '')
    if search:
        filters = []
        filters.append(ContainerStatus.name.ilike(f'%{search}%'))
        filters.append(ContainerStatus.description.ilike(f'%{search}%'))
        if filters:
            query = query.filter(or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(ContainerStatus, sort[1:]).desc())
    else:
        query = query.order_by(getattr(ContainerStatus, sort))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    items = query.limit(page_size + 1).offset((page - 1) * page_size).all()
    has_more = len(items) > page_size
    items = items[:page_size]
    
    columns = [
        {'key': 'name', 'label': 'Name', 'sortable': True},
        {'key': 'description', 'label': 'Description', 'sortable': True}
    ]

    if request.headers.get('HX-Request'):
        if request.args.get('page'):
            # Return only rows for "Load More"
            return render_template(
                'containerstatus/rows.html',
                items=items,
                routes=Routes(bp)
            )
        # Return the entire table for other HTMX requests
        return render_template(
            'containerstatus/table.html',
            items=items,
            columns=columns,
            routes=Routes(bp),
            search=search,
            sort=sort,
            page=page,
            has_more=has_more
        )

    return render_template(
        'containerstatus/list.html',
        items=items,
        columns=columns,
        routes=Routes(bp),
        search=search,
        sort=sort,
        page=page,
        has_more=has_more,
        page_size=page_size,
        entity_name='containerstatus'
    )

@bp.route('/containerstatus/new', methods=['GET'])
def create_form():
    return render_template(
        'containerstatus/form_modal.html',
        routes=Routes(bp)
    )

@bp.route('/containerstatus/<int:id>/edit', methods=['GET'])
def edit_form(id):
    item = ContainerStatus.query.get_or_404(id)
    return render_template(
        'containerstatus/form_modal.html',
        item=item,
        routes=Routes(bp)
    )

@bp.route('/containerstatus/new', methods=['POST'])
def create_containerstatus():
    item = ContainerStatus()
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    
    db_session.add(item)
    db_session.commit()
    
    return render_template(
        'containerstatus/table.html',
        items=ContainerStatus.query.all(),
        columns=columns,
        routes=Routes(bp),
        search='',
        sort='-id',
        page=1,
        has_more=False
    )

@bp.route('/containerstatus/<int:id>/edit', methods=['POST'])
def edit_containerstatus(id):
    item = ContainerStatus.query.get_or_404(id)
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    
    db_session.commit()
    
    return render_template(
        'containerstatus/table.html',
        items=ContainerStatus.query.all(),
        columns=columns,
        routes=Routes(bp),
        search='',
        sort='-id',
        page=1,
        has_more=False
    )

@bp.route('/containerstatus/<int:id>/delete', methods=['DELETE'])
def delete_containerstatus(id):
    item = ContainerStatus.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    
    return render_template(
        'containerstatus/table.html',
        items=ContainerStatus.query.all(),
        columns=columns,
        routes=Routes(bp),
        search='',
        sort='-id',
        page=1,
        has_more=False
    )
