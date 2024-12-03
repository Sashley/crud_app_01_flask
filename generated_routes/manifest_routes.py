
from flask import request, render_template, redirect, url_for
from database import db_session
from generated_models.manifest import Manifest

def register_manifest_routes(app):
    @app.route('/manifest')
    def list_manifest():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_manifest(query, offset, config.RECORDS_PER_PAGE) if query else get_manifest(offset, config.RECORDS_PER_PAGE)
        return render_template('manifest/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/manifest/create', methods=['GET', 'POST'])
    def create_manifest():
        if request.method == 'POST':
            bill_of_lading = request.form['bill_of_lading'] if request.form['bill_of_lading'] else None
            shipper_id = request.form['shipper_id'] if request.form['shipper_id'] else None
            consignee_id = request.form['consignee_id'] if request.form['consignee_id'] else None
            vessel_id = request.form['vessel_id'] if request.form['vessel_id'] else None
            voyage_id = request.form['voyage_id'] if request.form['voyage_id'] else None
            port_of_loading_id = request.form['port_of_loading_id'] if request.form['port_of_loading_id'] else None
            port_of_discharge_id = request.form['port_of_discharge_id'] if request.form['port_of_discharge_id'] else None
            place_of_delivery = request.form['place_of_delivery'] if request.form['place_of_delivery'] else None
            place_of_receipt = request.form['place_of_receipt'] if request.form['place_of_receipt'] else None
            clauses = request.form['clauses'] if request.form['clauses'] else None
            date_of_receipt = request.form['date_of_receipt'] if request.form['date_of_receipt'] else None
            manifester_id = request.form['manifester_id'] if request.form['manifester_id'] else None
            
            new_item = Manifest(
                bill_of_lading=bill_of_lading,
                shipper_id=shipper_id,
                consignee_id=consignee_id,
                vessel_id=vessel_id,
                voyage_id=voyage_id,
                port_of_loading_id=port_of_loading_id,
                port_of_discharge_id=port_of_discharge_id,
                place_of_delivery=place_of_delivery,
                place_of_receipt=place_of_receipt,
                clauses=clauses,
                date_of_receipt=date_of_receipt,
                manifester_id=manifester_id,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_manifest'))
        
        # Get related data for dropdowns
        clients = db_session.query(Client).all()
        clients = db_session.query(Client).all()
        vessels = db_session.query(Vessel).all()
        voyages = db_session.query(Voyage).all()
        ports = db_session.query(Port).all()
        ports = db_session.query(Port).all()
        users = db_session.query(User).all()
        
        return render_template('manifest/form.html', 
            mode='create',
            clients=clients,
            clients=clients,
            vessels=vessels,
            voyages=voyages,
            ports=ports,
            ports=ports,
            users=users,
        )

    @app.route('/manifest/<int:id>/edit', methods=['GET', 'POST'])
    def edit_manifest(id):
        item = db_session.get(Manifest, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.bill_of_lading = request.form['bill_of_lading'] if request.form['bill_of_lading'] else None
            item.shipper_id = request.form['shipper_id'] if request.form['shipper_id'] else None
            item.consignee_id = request.form['consignee_id'] if request.form['consignee_id'] else None
            item.vessel_id = request.form['vessel_id'] if request.form['vessel_id'] else None
            item.voyage_id = request.form['voyage_id'] if request.form['voyage_id'] else None
            item.port_of_loading_id = request.form['port_of_loading_id'] if request.form['port_of_loading_id'] else None
            item.port_of_discharge_id = request.form['port_of_discharge_id'] if request.form['port_of_discharge_id'] else None
            item.place_of_delivery = request.form['place_of_delivery'] if request.form['place_of_delivery'] else None
            item.place_of_receipt = request.form['place_of_receipt'] if request.form['place_of_receipt'] else None
            item.clauses = request.form['clauses'] if request.form['clauses'] else None
            item.date_of_receipt = request.form['date_of_receipt'] if request.form['date_of_receipt'] else None
            item.manifester_id = request.form['manifester_id'] if request.form['manifester_id'] else None
            
            db_session.commit()
            return redirect(url_for('list_manifest'))
        
        # Get related data for dropdowns
        clients = db_session.query(Client).all()
        clients = db_session.query(Client).all()
        vessels = db_session.query(Vessel).all()
        voyages = db_session.query(Voyage).all()
        ports = db_session.query(Port).all()
        ports = db_session.query(Port).all()
        users = db_session.query(User).all()
        
        return render_template('manifest/form.html', 
            item=item,
            mode='edit',
            clients=clients,
            clients=clients,
            vessels=vessels,
            voyages=voyages,
            ports=ports,
            ports=ports,
            users=users,
        )

    @app.route('/manifest/<int:id>/delete', methods=['POST'])
    def delete_manifest(id):
        item = db_session.get(Manifest, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_manifest'))

    def get_manifest(offset, limit):
        return db_session.query(Manifest).order_by(
            Manifest.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_manifest(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Manifest)\
            .filter(Manifest.bill_of_lading.ilike(search_term))\
            .order_by(Manifest.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()