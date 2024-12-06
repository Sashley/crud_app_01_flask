
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.voyage import Voyage

bp = Blueprint('voyage', __name__)

def register_voyage_routes(app):
    app.register_blueprint(bp)

@bp.route('/voyage')
def list_voyage():
    query = Voyage.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Voyage.name.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Voyage, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Voyage, sort))
    
    items = query.all()
    return render_template(
        'voyage/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/voyage/new', methods=['GET', 'POST'])
def create_voyage():
    if request.method == 'POST':
        item = Voyage()
        item.name = request.form.get('name')
        item.vessel_id = request.form.get('vessel_id')
        item.rotation_number = request.form.get('rotation_number')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('voyage.list_voyage'))
    
    return render_template('voyage/form.html')

@bp.route('/voyage/<int:id>/edit', methods=['GET', 'POST'])
def edit_voyage(id):
    item = Voyage.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.vessel_id = request.form.get('vessel_id')
        item.rotation_number = request.form.get('rotation_number')
        
        db_session.commit()
        return redirect(url_for('voyage.list_voyage'))
    
    return render_template('voyage/form.html', item=item)

@bp.route('/voyage/<int:id>/delete', methods=['POST'])
def delete_voyage(id):
    item = Voyage.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('voyage.list_voyage'))