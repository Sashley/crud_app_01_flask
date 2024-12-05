
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.rate import Rate

def register_rate_routes(app):
    @app.route('/rate')
    def list_rate():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_rate(query, offset, config.RECORDS_PER_PAGE) if query else get_rate(offset, config.RECORDS_PER_PAGE)
        return render_template('rate/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/rate/create', methods=['GET', 'POST'])
    def create_rate():
        if request.method == 'POST':
            distance = int(request.form['distance']) if request.form['distance'] else None
            commodity_id = request.form['commodity_id'] if request.form['commodity_id'] else None
            pack_type_id = request.form['pack_type_id'] if request.form['pack_type_id'] else None
            client_id = request.form['client_id'] if request.form['client_id'] else None
            rate = float(request.form['rate']) if request.form['rate'] else None
            effective = request.form['effective'] if request.form['effective'] else None
            
            new_item = Rate(
                distance=distance,
                commodity_id=commodity_id,
                pack_type_id=pack_type_id,
                client_id=client_id,
                rate=rate,
                effective=effective,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_rate'))
        
        # Get related data for dropdowns
        commoditys = db_session.query(Commodity).all()
        packtypes = db_session.query(Packtype).all()
        clients = db_session.query(Client).all()
        
        return render_template('rate/form.html', 
            mode='create',
            commoditys=commoditys,
            packtypes=packtypes,
            clients=clients,
        )

    @app.route('/rate/<int:id>/edit', methods=['GET', 'POST'])
    def edit_rate(id):
        item = db_session.get(Rate, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.distance = int(request.form['distance']) if request.form['distance'] else None
            item.commodity_id = request.form['commodity_id'] if request.form['commodity_id'] else None
            item.pack_type_id = request.form['pack_type_id'] if request.form['pack_type_id'] else None
            item.client_id = request.form['client_id'] if request.form['client_id'] else None
            item.rate = float(request.form['rate']) if request.form['rate'] else None
            item.effective = request.form['effective'] if request.form['effective'] else None
            
            db_session.commit()
            return redirect(url_for('list_rate'))
        
        # Get related data for dropdowns
        commoditys = db_session.query(Commodity).all()
        packtypes = db_session.query(Packtype).all()
        clients = db_session.query(Client).all()
        
        return render_template('rate/form.html', 
            item=item,
            mode='edit',
            commoditys=commoditys,
            packtypes=packtypes,
            clients=clients,
        )

    @app.route('/rate/<int:id>/delete', methods=['POST'])
    def delete_rate(id):
        item = db_session.get(Rate, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_rate'))

    def get_rate(offset, limit):
        return db_session.query(Rate).order_by(
            Rate.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_rate(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Rate)\
            .order_by(Rate.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()