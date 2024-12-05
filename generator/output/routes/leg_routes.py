
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.leg import Leg
import config

def register_leg_routes(app):
    @app.route('/leg')
    def list_leg():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_leg(query, offset, config.RECORDS_PER_PAGE) if query else get_leg(offset, config.RECORDS_PER_PAGE)
        return render_template('leg/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/leg/create', methods=['GET', 'POST'])
    def create_leg():
        if request.method == 'POST':
            voyage_id = request.form['voyage_id'] if request.form['voyage_id'] else None
            port_id = request.form['port_id'] if request.form['port_id'] else None
            leg_number = int(request.form['leg_number']) if request.form['leg_number'] else None
            eta = request.form['eta'] if request.form['eta'] else None
            etd = request.form['etd'] if request.form['etd'] else None
            
            new_item = Leg(
                voyage_id=voyage_id,
                port_id=port_id,
                leg_number=leg_number,
                eta=eta,
                etd=etd,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_leg'))
        
        # Get related data for dropdowns
        voyages = db_session.query(Voyage).all()
        ports = db_session.query(Port).all()
        
        return render_template('leg/form.html', 
            mode='create',
            voyages=voyages,
            ports=ports,
        )

    @app.route('/leg/<int:id>/edit', methods=['GET', 'POST'])
    def edit_leg(id):
        item = db_session.get(Leg, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.voyage_id = request.form['voyage_id'] if request.form['voyage_id'] else None
            item.port_id = request.form['port_id'] if request.form['port_id'] else None
            item.leg_number = int(request.form['leg_number']) if request.form['leg_number'] else None
            item.eta = request.form['eta'] if request.form['eta'] else None
            item.etd = request.form['etd'] if request.form['etd'] else None
            
            db_session.commit()
            return redirect(url_for('list_leg'))
        
        # Get related data for dropdowns
        voyages = db_session.query(Voyage).all()
        ports = db_session.query(Port).all()
        
        return render_template('leg/form.html', 
            item=item,
            mode='edit',
            voyages=voyages,
            ports=ports,
        )

    @app.route('/leg/<int:id>/delete', methods=['POST'])
    def delete_leg(id):
        item = db_session.get(Leg, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_leg'))

    def get_leg(offset, limit):
        return db_session.query(Leg).order_by(
            Leg.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_leg(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Leg)\
            .order_by(Leg.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()