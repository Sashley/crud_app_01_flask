
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.client import Client
from generator.output.models.country import Country
import config

def register_client_routes(app):
    @app.route('/client')
    def list_client():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_client(query, offset, config.RECORDS_PER_PAGE) if query else get_client(offset, config.RECORDS_PER_PAGE)
        return render_template('client/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/client/create', methods=['GET', 'POST'])
    def create_client():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            address = request.form['address'] if request.form['address'] else None
            town = request.form['town'] if request.form['town'] else None
            country_id = request.form['country_id'] if request.form['country_id'] else None
            contact_person = request.form['contact_person'] if request.form['contact_person'] else None
            email = request.form['email'] if request.form['email'] else None
            phone = request.form['phone'] if request.form['phone'] else None
            
            new_item = Client(
                name=name,
                address=address,
                town=town,
                country_id=country_id,
                contact_person=contact_person,
                email=email,
                phone=phone,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_client'))
        
        # Get related data for dropdowns
        countrys = db_session.query(Country).all()
        
        return render_template('client/form.html', 
            mode='create',
            countrys=countrys,
        )

    @app.route('/client/<int:id>/edit', methods=['GET', 'POST'])
    def edit_client(id):
        item = db_session.get(Client, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.address = request.form['address'] if request.form['address'] else None
            item.town = request.form['town'] if request.form['town'] else None
            item.country_id = request.form['country_id'] if request.form['country_id'] else None
            item.contact_person = request.form['contact_person'] if request.form['contact_person'] else None
            item.email = request.form['email'] if request.form['email'] else None
            item.phone = request.form['phone'] if request.form['phone'] else None
            
            db_session.commit()
            return redirect(url_for('list_client'))
        
        # Get related data for dropdowns
        countrys = db_session.query(Country).all()
        
        return render_template('client/form.html', 
            item=item,
            mode='edit',
            countrys=countrys,
        )

    @app.route('/client/<int:id>/delete', methods=['POST'])
    def delete_client(id):
        item = db_session.get(Client, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_client'))

    def get_client(offset, limit):
        return db_session.query(Client).order_by(
            Client.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_client(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Client)\
            .filter(Client.name.ilike(search_term))\
            .filter(Client.address.ilike(search_term))\
            .filter(Client.town.ilike(search_term))\
            .order_by(Client.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()