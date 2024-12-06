
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.container import Container

bp = Blueprint('container', __name__)

def register_container_routes(app):
    app.register_blueprint(bp)

@bp.route('/container')
def list_container():
    query = Container.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Container.number.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Container, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Container, sort))
    
    items = query.all()
    return render_template(
        'container/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/container/new', methods=['GET', 'POST'])
def create_container():
    if request.method == 'POST':
        item = Container()
        item.number = request.form.get('number')
        item.port_id = request.form.get('port_id')
        item.updated = request.form.get('updated')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('container.list_container'))
    
    return render_template('container/form.html')

@bp.route('/container/<int:id>/edit', methods=['GET', 'POST'])
def edit_container(id):
    item = Container.query.get_or_404(id)
    
    if request.method == 'POST':
        item.number = request.form.get('number')
        item.port_id = request.form.get('port_id')
        item.updated = request.form.get('updated')
        
        db_session.commit()
        return redirect(url_for('container.list_container'))
    
    return render_template('container/form.html', item=item)

@bp.route('/container/<int:id>/delete', methods=['POST'])
def delete_container(id):
    item = Container.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('container.list_container'))