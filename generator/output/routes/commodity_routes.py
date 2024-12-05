
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.commodity import Commodity
import config

def register_commodity_routes(app):
    @app.route('/commodity')
    def list_commodity():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_commodity(query, offset, config.RECORDS_PER_PAGE) if query else get_commodity(offset, config.RECORDS_PER_PAGE)
        return render_template('commodity/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/commodity/create', methods=['GET', 'POST'])
    def create_commodity():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            description = request.form['description'] if request.form['description'] else None
            
            new_item = Commodity(
                name=name,
                description=description,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_commodity'))
        
        # Get related data for dropdowns
        
        return render_template('commodity/form.html', 
            mode='create',
        )

    @app.route('/commodity/<int:id>/edit', methods=['GET', 'POST'])
    def edit_commodity(id):
        item = db_session.get(Commodity, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.description = request.form['description'] if request.form['description'] else None
            
            db_session.commit()
            return redirect(url_for('list_commodity'))
        
        # Get related data for dropdowns
        
        return render_template('commodity/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/commodity/<int:id>/delete', methods=['POST'])
    def delete_commodity(id):
        item = db_session.get(Commodity, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_commodity'))

    def get_commodity(offset, limit):
        return db_session.query(Commodity).order_by(
            Commodity.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_commodity(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Commodity)\
            .filter(Commodity.name.ilike(search_term))\
            .filter(Commodity.description.ilike(search_term))\
            .order_by(Commodity.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()