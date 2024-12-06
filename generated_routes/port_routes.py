
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.port import Port

bp = Blueprint('port', __name__)

def register_port_routes(app):
    app.register_blueprint(bp)

@bp.route('/port')
def list_port():
    query = Port.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Port.name.ilike(f'%{search}%'))
        filters.append(Port.prefix.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Port, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Port, sort))
    
    items = query.all()
    return render_template(
        'port/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/port/new', methods=['GET', 'POST'])
def create_port():
    if request.method == 'POST':
        item = Port()
        item.name = request.form.get('name')
        item.country_id = request.form.get('country_id')
        item.prefix = request.form.get('prefix')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('port.list_port'))
    
    return render_template('port/form.html')

@bp.route('/port/<int:id>/edit', methods=['GET', 'POST'])
def edit_port(id):
    item = Port.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.country_id = request.form.get('country_id')
        item.prefix = request.form.get('prefix')
        
        db_session.commit()
        return redirect(url_for('port.list_port'))
    
    return render_template('port/form.html', item=item)

@bp.route('/port/<int:id>/delete', methods=['POST'])
def delete_port(id):
    item = Port.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('port.list_port'))