
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.country import Country
import config

def register_country_routes(app):
    @app.route('/country')
    def list_country():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_country(query, offset, config.RECORDS_PER_PAGE) if query else get_country(offset, config.RECORDS_PER_PAGE)
        return render_template('country/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/country/create', methods=['GET', 'POST'])
    def create_country():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            
            new_item = Country(
                name=name,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_country'))
        
        # Get related data for dropdowns
        
        return render_template('country/form.html', 
            mode='create',
        )

    @app.route('/country/<int:id>/edit', methods=['GET', 'POST'])
    def edit_country(id):
        item = db_session.get(Country, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            
            db_session.commit()
            return redirect(url_for('list_country'))
        
        # Get related data for dropdowns
        
        return render_template('country/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/country/<int:id>/delete', methods=['POST'])
    def delete_country(id):
        item = db_session.get(Country, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_country'))

    def get_country(offset, limit):
        return db_session.query(Country).order_by(
            Country.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_country(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Country)\
            .filter(Country.name.ilike(search_term))\
            .order_by(Country.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()