
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.client import Client

bp = Blueprint('client', __name__)

def register_client_routes(app):
    app.register_blueprint(bp)

@bp.route('/client')
def list_client():
    query = Client.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Client.name.ilike(f'%{search}%'))
        filters.append(Client.address.ilike(f'%{search}%'))
        filters.append(Client.town.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Client, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Client, sort))
    
    items = query.all()
    return render_template(
        'client/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/client/new', methods=['GET', 'POST'])
def create_client():
    if request.method == 'POST':
        item = Client()
        item.name = request.form.get('name')
        item.address = request.form.get('address')
        item.town = request.form.get('town')
        item.country_id = request.form.get('country_id')
        item.contact_person = request.form.get('contact_person')
        item.email = request.form.get('email')
        item.phone = request.form.get('phone')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('client.list_client'))
    
    return render_template('client/form.html')

@bp.route('/client/<int:id>/edit', methods=['GET', 'POST'])
def edit_client(id):
    item = Client.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.address = request.form.get('address')
        item.town = request.form.get('town')
        item.country_id = request.form.get('country_id')
        item.contact_person = request.form.get('contact_person')
        item.email = request.form.get('email')
        item.phone = request.form.get('phone')
        
        db_session.commit()
        return redirect(url_for('client.list_client'))
    
    return render_template('client/form.html', item=item)

@bp.route('/client/<int:id>/delete', methods=['POST'])
def delete_client(id):
    item = Client.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('client.list_client'))