
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.voyage import Voyage

def register_voyage_routes(app):
    @app.route('/voyage')
    def list_voyage():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_voyage(query, offset, config.RECORDS_PER_PAGE) if query else get_voyage(offset, config.RECORDS_PER_PAGE)
        return render_template('voyage/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/voyage/create', methods=['GET', 'POST'])
    def create_voyage():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            vessel_id = request.form['vessel_id'] if request.form['vessel_id'] else None
            rotation_number = int(request.form['rotation_number']) if request.form['rotation_number'] else None
            
            new_item = Voyage(
                name=name,
                vessel_id=vessel_id,
                rotation_number=rotation_number,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_voyage'))
        
        # Get related data for dropdowns
        vessels = db_session.query(Vessel).all()
        
        return render_template('voyage/form.html', 
            mode='create',
            vessels=vessels,
        )

    @app.route('/voyage/<int:id>/edit', methods=['GET', 'POST'])
    def edit_voyage(id):
        item = db_session.get(Voyage, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.vessel_id = request.form['vessel_id'] if request.form['vessel_id'] else None
            item.rotation_number = int(request.form['rotation_number']) if request.form['rotation_number'] else None
            
            db_session.commit()
            return redirect(url_for('list_voyage'))
        
        # Get related data for dropdowns
        vessels = db_session.query(Vessel).all()
        
        return render_template('voyage/form.html', 
            item=item,
            mode='edit',
            vessels=vessels,
        )

    @app.route('/voyage/<int:id>/delete', methods=['POST'])
    def delete_voyage(id):
        item = db_session.get(Voyage, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_voyage'))

    def get_voyage(offset, limit):
        return db_session.query(Voyage).order_by(
            Voyage.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_voyage(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Voyage)\
            .filter(Voyage.name.ilike(search_term))\
            .order_by(Voyage.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()