from flask import Blueprint, render_template, request, redirect, url_for, abort
from database import db_session
from generated_models.voyage import Voyage
from generated_models.vessel import Vessel
from sqlalchemy import or_, select, func

bp = Blueprint('voyage', __name__)

routes = {
    'list': 'voyage.list_voyage',
    'create': 'voyage.create_voyage',
    'edit': 'voyage.edit_voyage',
    'delete': 'voyage.delete_voyage',
    'load_form': 'voyage.load_form'
}

def register_voyage_routes(app):
    app.register_blueprint(bp)

@bp.route('/voyage')
def list_voyage():
    # Start with a base query
    base_query = select(Voyage)
    
    # Apply search filters
    search = request.args.get('search', '')
    if search:
        filters = []
        filters.append(Voyage.voyage_number.ilike(f'%{search}%'))
        if filters:
            base_query = base_query.where(or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        base_query = base_query.order_by(getattr(Voyage, sort[1:]).desc())
    else:
        base_query = base_query.order_by(getattr(Voyage, sort))
    
    # Execute query and handle pagination
    page_size = int(request.args.get('page_size', '10'))
    page = int(request.args.get('page', '1'))
    offset = (page - 1) * page_size
    
    # Get total count
    total_count = db_session.scalar(select(func.count()).select_from(base_query.subquery()))
    
    # Get paginated items
    items = db_session.scalars(base_query.offset(offset).limit(page_size)).all()
    
    template_vars = {
        'items': items,
        'search': request.args.get('search', ''),
        'sort': request.args.get('sort', '-id'),
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'has_more': total_count > (page * page_size),
        'entity_name': 'voyage',
        'routes': {
            'list': 'voyage.list_voyage',
            'create': 'voyage.create_voyage',
            'edit': 'voyage.edit_voyage',
            'delete': 'voyage.delete_voyage'
        },
        'columns': [
            {
                'key': 'voyage_number',
                'label': 'Voyage Number',
                'sortable': True,
                'class': 'w-[100px] sm:w-[160px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                'width_class': 'max-w-[150px] sm:max-w-[170px]'
            },
            {
                'key': 'vessel_name',
                'label': 'Vessel',
                'sortable': True,
                'class': 'w-[160px] sm:w-[180px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                'responsive_class': 'hidden sm:table-cell',
                'width_class': 'max-w-[150px] sm:max-w-[170px]'
            },
            {
                'key': 'departure_date',
                'label': 'Departure Date',
                'sortable': True,
                'class': 'w-[140px] sm:w-[160px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                'responsive_class': 'hidden md:table-cell',
                'width_class': 'max-w-[130px] sm:max-w-[150px]'
            },
            {
                'key': 'arrival_date',
                'label': 'Arrival Date',
                'sortable': True,
                'class': 'w-[140px] sm:w-[160px] px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50',
                'responsive_class': 'hidden lg:table-cell',
                'width_class': 'max-w-[130px] sm:max-w-[150px]'
            }
        ],
        'identifier_field': 'voyage_number'
    }
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if is_htmx and page > 1:
        return render_template('voyage/rows.html', **template_vars)
    elif is_htmx:
        return render_template('voyage/table.html', **template_vars)
    
    return render_template('voyage/list.html', **template_vars)

@bp.route('/voyage/load_form', methods=['GET'])
def load_form():
    id = request.args.get('id')
    vessels = db_session.scalars(select(Vessel)).all()
    if id:
        stmt = select(Voyage).where(Voyage.id == id)
        item = db_session.scalar(stmt)
        if not item:
            abort(404)
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
    stmt = select(Voyage).where(Voyage.id == id)
    item = db_session.scalar(stmt)
    if not item:
        abort(404)
    
    item.voyage_number = request.form.get('voyage_number')
    item.vessel_id = request.form.get('vessel_id')
    item.departure_date = request.form.get('departure_date')
    item.arrival_date = request.form.get('arrival_date')
    
    db_session.commit()
    return '', 204

@bp.route('/voyage/<int:id>/delete', methods=['POST'])
def delete_voyage(id):
    stmt = select(Voyage).where(Voyage.id == id)
    item = db_session.scalar(stmt)
    if not item:
        abort(404)
    
    db_session.delete(item)
    db_session.commit()
    return '', 204

@bp.route('/voyage/empty', methods=['GET'])
def empty():
    return ''
