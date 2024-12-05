
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.shippingcompany import ShippingCompany
import config

def register_shippingcompany_routes(app):
    @app.route('/shippingcompany')
    def list_shippingcompany():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_shippingcompany(query, offset, config.RECORDS_PER_PAGE) if query else get_shippingcompany(offset, config.RECORDS_PER_PAGE)
        return render_template('shippingcompany/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/shippingcompany/create', methods=['GET', 'POST'])
    def create_shippingcompany():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            
            new_item = ShippingCompany(
                name=name,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_shippingcompany'))
        
        # Get related data for dropdowns
        
        return render_template('shippingcompany/form.html', 
            mode='create',
        )

    @app.route('/shippingcompany/<int:id>/edit', methods=['GET', 'POST'])
    def edit_shippingcompany(id):
        item = db_session.get(ShippingCompany, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            
            db_session.commit()
            return redirect(url_for('list_shippingcompany'))
        
        # Get related data for dropdowns
        
        return render_template('shippingcompany/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/shippingcompany/<int:id>/delete', methods=['POST'])
    def delete_shippingcompany(id):
        item = db_session.get(ShippingCompany, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_shippingcompany'))

    def get_shippingcompany(offset, limit):
        return db_session.query(ShippingCompany).order_by(
            ShippingCompany.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_shippingcompany(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(ShippingCompany)\
            .filter(ShippingCompany.name.ilike(search_term))\
            .order_by(ShippingCompany.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()