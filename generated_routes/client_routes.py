from flask import Blueprint, render_template, request, redirect, url_for, abort, make_response, jsonify
from database import db_session
from generated_models.client import Client
from generated_models.country import Country
from sqlalchemy import or_ as db_or
import json

bp = Blueprint('client', __name__)

def register_client_routes(app):
    app.register_blueprint(bp)

@bp.route('/client/empty')
def empty():
    """Return an empty response for closing modals"""
    response = make_response('')
    response.headers['HX-Trigger'] = 'modalClosed'
    return response

@bp.route('/client')
def list_client():
    # Debug request information
    print("\n=== Request Information ===")
    print(f"URL: {request.url}")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Args: {dict(request.args)}")
    
    query = Client.query.join(Client.country)
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Client.name.ilike(f'%{search}%'))
        filters.append(Client.address.ilike(f'%{search}%'))
        filters.append(Client.town.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db_or(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Client, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Client, sort))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    offset = (page - 1) * page_size
    
    # Get paginated items
    total_count = query.count()
    items = query.offset(offset).limit(page_size).all()
    
    # Add country_name to each item
    for item in items:
        item.country_name = item.country.name if item.country else 'N/A'
    
    has_more = (offset + len(items)) < total_count

    template_vars = {
        'items': items,
        'search': search,
        'sort': sort,
        'page': page,
        'page_size': page_size,
        'has_more': has_more,
        'entity_name': 'Client',
        'identifier_field': 'name',  # Added this line
        'routes': {
            'list': 'client.list_client',
            'create': 'client.save_client',
            'edit': 'client.load_form',
            'delete': 'client.delete_client'
        },
        'columns': [  # Added columns configuration
            {
                'key': 'name',
                'label': 'Name',
                'sortable': True,
                'class': 'px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50'
            },
            {
                'key': 'address',
                'label': 'Address',
                'sortable': True,
                'class': 'hidden lg:table-cell px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50'
            },
            {
                'key': 'town',
                'label': 'Town',
                'sortable': True,
                'class': 'hidden xl:table-cell px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50'
            },
            {
                'key': 'country_name',
                'label': 'Country',
                'sortable': True,
                'class': 'hidden 2xl:table-cell px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50'
            },
            {
                'key': 'contact_person',
                'label': 'Contact Person',
                'sortable': True,
                'class': 'hidden 2xl:table-cell px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50'
            }
        ]
    }

    # Handle HTMX requests differently
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    # Debug response information
    print("\n=== Response Information ===")
    print(f"Is HTMX Request: {is_htmx}")
    print(f"Page > 1: {page > 1}")
    
    if is_htmx:
        if page > 1:
            # For load more, just return the rows without any wrapping elements
            print("Rendering rows template for load more")
            response = make_response(render_template('client/rows.html', **template_vars))
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': f'Loaded {len(items)} more items'
            })
            return response
        else:
            # For other HTMX requests (search, sort, etc.), return the full table
            print("Rendering full table template for HTMX request")
            return render_template('client/table.html', **template_vars)
    
    # For regular page load, return the full list template
    print("Rendering full list template for regular request")
    return render_template('client/list.html', **template_vars)

@bp.route('/client/load-form')
def load_form():
    """Load the form content via HTMX"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(Client).get(id)
            if item is None:
                abort(404)
        else:
            item = None
            
        # Get all countries for the dropdown
        countries = db_session.query(Country).order_by(Country.name).all()
        return render_template('client/form_modal.html', item=item, countries=countries)
    except Exception as e:
        db_session.rollback()
        raise

@bp.route('/client/save', methods=['POST'])
def save_client():
    """Save client via HTMX form submission"""
    try:
        id = request.args.get('id')
        if id:
            item = db_session.query(Client).get(id)
            if item is None:
                abort(404)
        else:
            item = Client()
            
        item.name = request.form.get('name')
        item.address = request.form.get('address')
        item.town = request.form.get('town')
        item.country_id = request.form.get('country_id')
        item.contact_person = request.form.get('contact_person')
        item.email = request.form.get('email')
        item.phone = request.form.get('phone')
        
        if not id:
            db_session.add(item)
        db_session.commit()
        
        # Create response with HX-Trigger header
        response = make_response('')
        response.headers['HX-Trigger'] = 'modalClosed'
        return response
    except Exception as e:
        db_session.rollback()
        raise

@bp.route('/client/<int:id>/delete', methods=['POST'])
def delete_client(id):
    try:
        item = db_session.query(Client).get_or_404(id)
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('client.list_client'))
    except Exception as e:
        db_session.rollback()
        raise
