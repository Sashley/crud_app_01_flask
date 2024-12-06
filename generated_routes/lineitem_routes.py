
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.lineitem import LineItem

bp = Blueprint('lineitem', __name__)

def register_lineitem_routes(app):
    app.register_blueprint(bp)

@bp.route('/lineitem')
def list_lineitem():
    query = LineItem.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(LineItem.description.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(LineItem, sort[1:]).desc())
    else:
        query = query.order_by(getattr(LineItem, sort))
    
    items = query.all()
    return render_template(
        'lineitem/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/lineitem/new', methods=['GET', 'POST'])
def create_lineitem():
    if request.method == 'POST':
        item = LineItem()
        item.manifest_id = request.form.get('manifest_id')
        item.description = request.form.get('description')
        item.quantity = request.form.get('quantity')
        item.weight = request.form.get('weight')
        item.volume = request.form.get('volume')
        item.pack_type_id = request.form.get('pack_type_id')
        item.commodity_id = request.form.get('commodity_id')
        item.container_id = request.form.get('container_id')
        item.manifester_id = request.form.get('manifester_id')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('lineitem.list_lineitem'))
    
    return render_template('lineitem/form.html')

@bp.route('/lineitem/<int:id>/edit', methods=['GET', 'POST'])
def edit_lineitem(id):
    item = LineItem.query.get_or_404(id)
    
    if request.method == 'POST':
        item.manifest_id = request.form.get('manifest_id')
        item.description = request.form.get('description')
        item.quantity = request.form.get('quantity')
        item.weight = request.form.get('weight')
        item.volume = request.form.get('volume')
        item.pack_type_id = request.form.get('pack_type_id')
        item.commodity_id = request.form.get('commodity_id')
        item.container_id = request.form.get('container_id')
        item.manifester_id = request.form.get('manifester_id')
        
        db_session.commit()
        return redirect(url_for('lineitem.list_lineitem'))
    
    return render_template('lineitem/form.html', item=item)

@bp.route('/lineitem/<int:id>/delete', methods=['POST'])
def delete_lineitem(id):
    item = LineItem.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('lineitem.list_lineitem'))