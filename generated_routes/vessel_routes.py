
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.vessel import Vessel

bp = Blueprint('vessel', __name__)

def register_vessel_routes(app):
    app.register_blueprint(bp)

@bp.route('/vessel')
def list_vessel():
    query = Vessel.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Vessel.name.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Vessel, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Vessel, sort))
    
    items = query.all()
    return render_template(
        'vessel/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/vessel/new', methods=['GET', 'POST'])
def create_vessel():
    if request.method == 'POST':
        item = Vessel()
        item.name = request.form.get('name')
        item.shipping_company_id = request.form.get('shipping_company_id')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('vessel.list_vessel'))
    
    return render_template('vessel/form.html')

@bp.route('/vessel/<int:id>/edit', methods=['GET', 'POST'])
def edit_vessel(id):
    item = Vessel.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.shipping_company_id = request.form.get('shipping_company_id')
        
        db_session.commit()
        return redirect(url_for('vessel.list_vessel'))
    
    return render_template('vessel/form.html', item=item)

@bp.route('/vessel/<int:id>/delete', methods=['POST'])
def delete_vessel(id):
    item = Vessel.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('vessel.list_vessel'))