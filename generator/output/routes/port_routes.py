
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.port import Port
from generator.output.models.country import Country
import config

def register_port_routes(app):
    @app.route('/port')
    def list_port():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_port(query, offset, config.RECORDS_PER_PAGE) if query else get_port(offset, config.RECORDS_PER_PAGE)
        return render_template('port/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/port/create', methods=['GET', 'POST'])
    def create_port():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            country_id = request.form['country_id'] if request.form['country_id'] else None
            prefix = request.form['prefix'] if request.form['prefix'] else None
            
            new_item = Port(
                name=name,
                country_id=country_id,
                prefix=prefix,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_port'))
        
        # Get related data for dropdowns
        countrys = db_session.query(Country).all()
        
        return render_template('port/form.html', 
            mode='create',
            countrys=countrys,
        )

    @app.route('/port/<int:id>/edit', methods=['GET', 'POST'])
    def edit_port(id):
        item = db_session.get(Port, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.country_id = request.form['country_id'] if request.form['country_id'] else None
            item.prefix = request.form['prefix'] if request.form['prefix'] else None
            
            db_session.commit()
            return redirect(url_for('list_port'))
        
        # Get related data for dropdowns
        countrys = db_session.query(Country).all()
        
        return render_template('port/form.html', 
            item=item,
            mode='edit',
            countrys=countrys,
        )

    @app.route('/port/<int:id>/delete', methods=['POST'])
    def delete_port(id):
        item = db_session.get(Port, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_port'))

    def get_port(offset, limit):
        return db_session.query(Port).order_by(
            Port.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_port(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Port)\
            .filter(Port.name.ilike(search_term))\
            .filter(Port.prefix.ilike(search_term))\
            .order_by(Port.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()