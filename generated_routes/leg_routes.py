
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.leg import Leg

bp = Blueprint('leg', __name__)

def register_leg_routes(app):
    app.register_blueprint(bp)

@bp.route('/leg')
def list_leg():
    query = Leg.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Leg, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Leg, sort))
    
    items = query.all()
    return render_template(
        'leg/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/leg/new', methods=['GET', 'POST'])
def create_leg():
    if request.method == 'POST':
        item = Leg()
        item.voyage_id = request.form.get('voyage_id')
        item.port_id = request.form.get('port_id')
        item.leg_number = request.form.get('leg_number')
        item.eta = request.form.get('eta')
        item.etd = request.form.get('etd')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('leg.list_leg'))
    
    return render_template('leg/form.html')

@bp.route('/leg/<int:id>/edit', methods=['GET', 'POST'])
def edit_leg(id):
    item = Leg.query.get_or_404(id)
    
    if request.method == 'POST':
        item.voyage_id = request.form.get('voyage_id')
        item.port_id = request.form.get('port_id')
        item.leg_number = request.form.get('leg_number')
        item.eta = request.form.get('eta')
        item.etd = request.form.get('etd')
        
        db_session.commit()
        return redirect(url_for('leg.list_leg'))
    
    return render_template('leg/form.html', item=item)

@bp.route('/leg/<int:id>/delete', methods=['POST'])
def delete_leg(id):
    item = Leg.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('leg.list_leg'))