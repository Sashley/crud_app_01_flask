
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.country import Country

bp = Blueprint('country', __name__)

def register_country_routes(app):
    app.register_blueprint(bp)

@bp.route('/country')
def list_country():
    query = Country.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(Country.name.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Country, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Country, sort))
    
    items = query.all()
    return render_template(
        'country/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/country/new', methods=['GET', 'POST'])
def create_country():
    if request.method == 'POST':
        item = Country()
        item.name = request.form.get('name')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('country.list_country'))
    
    return render_template('country/form.html')

@bp.route('/country/<int:id>/edit', methods=['GET', 'POST'])
def edit_country(id):
    item = Country.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        
        db_session.commit()
        return redirect(url_for('country.list_country'))
    
    return render_template('country/form.html', item=item)

@bp.route('/country/<int:id>/delete', methods=['POST'])
def delete_country(id):
    item = Country.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('country.list_country'))