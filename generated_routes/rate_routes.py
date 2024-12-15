from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db_session
from generated_models.rate import Rate
from generated_models.commodity import Commodity
from generated_models.packtype import PackType
from generated_models.client import Client
from sqlalchemy import or_

bp = Blueprint('rate', __name__)

def register_rate_routes(app):
    app.register_blueprint(bp)

@bp.route('/rate')
def list_rate():
    query = Rate.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        if filters:
            query = query.filter(or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(Rate, sort[1:]).desc())
    else:
        query = query.order_by(getattr(Rate, sort))
    
    items = query.all()
    return render_template(
        'rate/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/rate/new', methods=['GET', 'POST'])
def create_rate():
    if request.method == 'POST':
        try:
            distance_code = int(request.form.get('distance_code', 0))
            if not 1 <= distance_code <= 8:
                flash('Distance code must be between 1 and 8', 'error')
                return render_template('rate/form.html', 
                                    commodities=Commodity.query.all(),
                                    pack_types=PackType.query.all(),
                                    clients=Client.query.all())

            item = Rate()
            item.distance_code = distance_code
            item.commodity_id = request.form.get('commodity_id')
            item.pack_type_id = request.form.get('pack_type_id')
            item.client_id = request.form.get('client_id') or None  # Convert empty string to None
            item.rate = request.form.get('rate', type=float)
            item.effective = request.form.get('effective')
            
            db_session.add(item)
            db_session.commit()
            return redirect(url_for('rate.list_rate'))
        except ValueError:
            flash('Invalid input values', 'error')
            return render_template('rate/form.html',
                                commodities=Commodity.query.all(),
                                pack_types=PackType.query.all(),
                                clients=Client.query.all())
    
    return render_template('rate/form.html',
                         commodities=Commodity.query.all(),
                         pack_types=PackType.query.all(),
                         clients=Client.query.all())

@bp.route('/rate/<int:id>/edit', methods=['GET', 'POST'])
def edit_rate(id):
    item = Rate.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            distance_code = int(request.form.get('distance_code', 0))
            if not 1 <= distance_code <= 8:
                flash('Distance code must be between 1 and 8', 'error')
                return render_template('rate/form.html', 
                                    item=item,
                                    commodities=Commodity.query.all(),
                                    pack_types=PackType.query.all(),
                                    clients=Client.query.all())

            item.distance_code = distance_code
            item.commodity_id = request.form.get('commodity_id')
            item.pack_type_id = request.form.get('pack_type_id')
            item.client_id = request.form.get('client_id') or None  # Convert empty string to None
            item.rate = request.form.get('rate', type=float)
            item.effective = request.form.get('effective')
            
            db_session.commit()
            return redirect(url_for('rate.list_rate'))
        except ValueError:
            flash('Invalid input values', 'error')
            return render_template('rate/form.html', 
                                item=item,
                                commodities=Commodity.query.all(),
                                pack_types=PackType.query.all(),
                                clients=Client.query.all())
    
    return render_template('rate/form.html', 
                         item=item,
                         commodities=Commodity.query.all(),
                         pack_types=PackType.query.all(),
                         clients=Client.query.all())

@bp.route('/rate/<int:id>/delete', methods=['POST'])
def delete_rate(id):
    item = Rate.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('rate.list_rate'))
