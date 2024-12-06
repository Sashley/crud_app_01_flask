
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.containerstatus import ContainerStatus

bp = Blueprint('containerstatus', __name__)

def register_containerstatus_routes(app):
    app.register_blueprint(bp)

@bp.route('/containerstatus')
def list_containerstatus():
    query = ContainerStatus.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(ContainerStatus.name.ilike(f'%{search}%'))
        filters.append(ContainerStatus.description.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(ContainerStatus, sort[1:]).desc())
    else:
        query = query.order_by(getattr(ContainerStatus, sort))
    
    items = query.all()
    return render_template(
        'containerstatus/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/containerstatus/new', methods=['GET', 'POST'])
def create_containerstatus():
    if request.method == 'POST':
        item = ContainerStatus()
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('containerstatus.list_containerstatus'))
    
    return render_template('containerstatus/form.html')

@bp.route('/containerstatus/<int:id>/edit', methods=['GET', 'POST'])
def edit_containerstatus(id):
    item = ContainerStatus.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.commit()
        return redirect(url_for('containerstatus.list_containerstatus'))
    
    return render_template('containerstatus/form.html', item=item)

@bp.route('/containerstatus/<int:id>/delete', methods=['POST'])
def delete_containerstatus(id):
    item = ContainerStatus.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('containerstatus.list_containerstatus'))