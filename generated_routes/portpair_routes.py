
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.portpair import PortPair

bp = Blueprint('portpair', __name__)

def register_portpair_routes(app):
    app.register_blueprint(bp)

@bp.route('/portpair')
def list_portpair():
    query = PortPair.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(PortPair, sort[1:]).desc())
    else:
        query = query.order_by(getattr(PortPair, sort))
    
    items = query.all()
    return render_template(
        'portpair/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/portpair/new', methods=['GET', 'POST'])
def create_portpair():
    if request.method == 'POST':
        item = PortPair()
        item.pol_id = request.form.get('pol_id')
        item.pod_id = request.form.get('pod_id')
        item.distance = request.form.get('distance')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('portpair.list_portpair'))
    
    return render_template('portpair/form.html')

@bp.route('/portpair/<int:id>/edit', methods=['GET', 'POST'])
def edit_portpair(id):
    item = PortPair.query.get_or_404(id)
    
    if request.method == 'POST':
        item.pol_id = request.form.get('pol_id')
        item.pod_id = request.form.get('pod_id')
        item.distance = request.form.get('distance')
        
        db_session.commit()
        return redirect(url_for('portpair.list_portpair'))
    
    return render_template('portpair/form.html', item=item)

@bp.route('/portpair/<int:id>/delete', methods=['POST'])
def delete_portpair(id):
    item = PortPair.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('portpair.list_portpair'))