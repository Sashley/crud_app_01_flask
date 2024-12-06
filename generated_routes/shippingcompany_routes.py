
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.shippingcompany import ShippingCompany

bp = Blueprint('shippingcompany', __name__)

def register_shippingcompany_routes(app):
    app.register_blueprint(bp)

@bp.route('/shippingcompany')
def list_shippingcompany():
    query = ShippingCompany.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(ShippingCompany.name.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(ShippingCompany, sort[1:]).desc())
    else:
        query = query.order_by(getattr(ShippingCompany, sort))
    
    items = query.all()
    return render_template(
        'shippingcompany/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/shippingcompany/new', methods=['GET', 'POST'])
def create_shippingcompany():
    if request.method == 'POST':
        item = ShippingCompany()
        item.name = request.form.get('name')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('shippingcompany.list_shippingcompany'))
    
    return render_template('shippingcompany/form.html')

@bp.route('/shippingcompany/<int:id>/edit', methods=['GET', 'POST'])
def edit_shippingcompany(id):
    item = ShippingCompany.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        
        db_session.commit()
        return redirect(url_for('shippingcompany.list_shippingcompany'))
    
    return render_template('shippingcompany/form.html', item=item)

@bp.route('/shippingcompany/<int:id>/delete', methods=['POST'])
def delete_shippingcompany(id):
    item = ShippingCompany.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('shippingcompany.list_shippingcompany'))