from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database import db_session
from generated_models.voyage import Voyage
from generated_models.vessel import Vessel
from sqlalchemy import or_

bp = Blueprint('voyage', __name__)

routes = {
    'list': 'voyage.list_voyage',
    'create': 'voyage.create_voyage',
    'edit': 'voyage.edit_voyage',
    'delete': 'voyage.delete_voyage',
    'load_form': 'voyage.load_form'
}

columns = [
    {'key': 'voyage_number', 'label': 'Voyage Number', 'sortable': True},
    {'key': 'vessel_name', 'label': 'Vessel', 'sortable': True, 'responsive_class': 'hidden sm:table-cell'},
    {'key': 'departure_date', 'label': 'Departure Date', 'sortable': True, 'responsive_class': 'hidden md:table-cell'},
    {'key': 'arrival_date', 'label': 'Arrival Date', 'sortable': True, 'responsive_class': 'hidden lg:table-cell'}
]

def register_voyage_routes(app):
    app.register_blueprint(bp)

@bp.route('/voyage')
def list_voyage():
    query = Voyage.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Voyage.voyage_number.ilike(f'%{search}%'))
        if filters:
            query = query.filter(or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Voyage, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Voyage, sort))
    
    items = query.all()
    
    if request.headers.get('HX-Request'):
        return render_template(
            'voyage/table.html',
            items=items,
            columns=columns,
            routes=routes,
            search=search,
            sort=sort
        )
    
    return render_template(
        'voyage/list.html',
        items=items,
        columns=columns,
        routes=routes,
        search=search,
        sort=sort
    )

@bp.route('/voyage/load_form', methods=['GET'])
def load_form():
    id = request.args.get('id')
    vessels = Vessel.query.all()
    if id:
        item = Voyage.query.get_or_404(id)
        return render_template('voyage/form_modal.html', item=item, vessels=vessels, routes=routes)
    return render_template('voyage/form_modal.html', vessels=vessels, routes=routes)

@bp.route('/voyage/new', methods=['POST'])
def create_voyage():
    item = Voyage()
    item.voyage_number = request.form.get('voyage_number')
    item.vessel_id = request.form.get('vessel_id')
    item.departure_date = request.form.get('departure_date')
    item.arrival_date = request.form.get('arrival_date')
    
    db_session.add(item)
    db_session.commit()
    
    return '', 204

@bp.route('/voyage/<int:id>/edit', methods=['POST'])
def edit_voyage(id):
    item = Voyage.query.get_or_404(id)
    
    item.voyage_number = request.form.get('voyage_number')
    item.vessel_id = request.form.get('vessel_id')
    item.departure_date = request.form.get('departure_date')
    item.arrival_date = request.form.get('arrival_date')
    
    db_session.commit()
    return '', 204

@bp.route('/voyage/<int:id>/delete', methods=['POST'])
def delete_voyage(id):
    item = Voyage.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return '', 204

@bp.route('/voyage/empty', methods=['GET'])
def empty():
    return ''
