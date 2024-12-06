
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.commodity import Commodity

bp = Blueprint('commodity', __name__)

def register_commodity_routes(app):
    app.register_blueprint(bp)

@bp.route('/commodity')
def list_commodity():
    query = Commodity.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Commodity.name.ilike(f'%{search}%'))
        filters.append(Commodity.description.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Commodity, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Commodity, sort))
    
    items = query.all()
    return render_template(
        'commodity/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/commodity/new', methods=['GET', 'POST'])
def create_commodity():
    if request.method == 'POST':
        item = Commodity()
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('commodity.list_commodity'))
    
    return render_template('commodity/form.html')

@bp.route('/commodity/<int:id>/edit', methods=['GET', 'POST'])
def edit_commodity(id):
    item = Commodity.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.commit()
        return redirect(url_for('commodity.list_commodity'))
    
    return render_template('commodity/form.html', item=item)

@bp.route('/commodity/<int:id>/delete', methods=['POST'])
def delete_commodity(id):
    item = Commodity.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('commodity.list_commodity'))