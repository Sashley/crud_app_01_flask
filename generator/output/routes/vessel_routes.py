
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.vessel import Vessel
import config

def register_vessel_routes(app):
    @app.route('/vessel')
    def list_vessel():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_vessel(query, offset, config.RECORDS_PER_PAGE) if query else get_vessel(offset, config.RECORDS_PER_PAGE)
        return render_template('vessel/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/vessel/create', methods=['GET', 'POST'])
    def create_vessel():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            shipping_company_id = request.form['shipping_company_id'] if request.form['shipping_company_id'] else None
            
            new_item = Vessel(
                name=name,
                shipping_company_id=shipping_company_id,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_vessel'))
        
        # Get related data for dropdowns
        shippingcompanys = db_session.query(Shippingcompany).all()
        
        return render_template('vessel/form.html', 
            mode='create',
            shippingcompanys=shippingcompanys,
        )

    @app.route('/vessel/<int:id>/edit', methods=['GET', 'POST'])
    def edit_vessel(id):
        item = db_session.get(Vessel, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.shipping_company_id = request.form['shipping_company_id'] if request.form['shipping_company_id'] else None
            
            db_session.commit()
            return redirect(url_for('list_vessel'))
        
        # Get related data for dropdowns
        shippingcompanys = db_session.query(Shippingcompany).all()
        
        return render_template('vessel/form.html', 
            item=item,
            mode='edit',
            shippingcompanys=shippingcompanys,
        )

    @app.route('/vessel/<int:id>/delete', methods=['POST'])
    def delete_vessel(id):
        item = db_session.get(Vessel, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_vessel'))

    def get_vessel(offset, limit):
        return db_session.query(Vessel).order_by(
            Vessel.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_vessel(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Vessel)\
            .filter(Vessel.name.ilike(search_term))\
            .order_by(Vessel.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()