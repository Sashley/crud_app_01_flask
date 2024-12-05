
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.lineitem import LineItem
import config

def register_lineitem_routes(app):
    @app.route('/lineitem')
    def list_lineitem():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_lineitem(query, offset, config.RECORDS_PER_PAGE) if query else get_lineitem(offset, config.RECORDS_PER_PAGE)
        return render_template('lineitem/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/lineitem/create', methods=['GET', 'POST'])
    def create_lineitem():
        if request.method == 'POST':
            manifest_id = request.form['manifest_id'] if request.form['manifest_id'] else None
            description = request.form['description'] if request.form['description'] else None
            quantity = int(request.form['quantity']) if request.form['quantity'] else None
            weight = int(request.form['weight']) if request.form['weight'] else None
            volume = int(request.form['volume']) if request.form['volume'] else None
            pack_type_id = request.form['pack_type_id'] if request.form['pack_type_id'] else None
            commodity_id = request.form['commodity_id'] if request.form['commodity_id'] else None
            container_id = request.form['container_id'] if request.form['container_id'] else None
            manifester_id = request.form['manifester_id'] if request.form['manifester_id'] else None
            
            new_item = LineItem(
                manifest_id=manifest_id,
                description=description,
                quantity=quantity,
                weight=weight,
                volume=volume,
                pack_type_id=pack_type_id,
                commodity_id=commodity_id,
                container_id=container_id,
                manifester_id=manifester_id,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_lineitem'))
        
        # Get related data for dropdowns
        manifests = db_session.query(Manifest).all()
        packtypes = db_session.query(Packtype).all()
        commoditys = db_session.query(Commodity).all()
        containers = db_session.query(Container).all()
        users = db_session.query(User).all()
        
        return render_template('lineitem/form.html', 
            mode='create',
            manifests=manifests,
            packtypes=packtypes,
            commoditys=commoditys,
            containers=containers,
            users=users,
        )

    @app.route('/lineitem/<int:id>/edit', methods=['GET', 'POST'])
    def edit_lineitem(id):
        item = db_session.get(LineItem, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.manifest_id = request.form['manifest_id'] if request.form['manifest_id'] else None
            item.description = request.form['description'] if request.form['description'] else None
            item.quantity = int(request.form['quantity']) if request.form['quantity'] else None
            item.weight = int(request.form['weight']) if request.form['weight'] else None
            item.volume = int(request.form['volume']) if request.form['volume'] else None
            item.pack_type_id = request.form['pack_type_id'] if request.form['pack_type_id'] else None
            item.commodity_id = request.form['commodity_id'] if request.form['commodity_id'] else None
            item.container_id = request.form['container_id'] if request.form['container_id'] else None
            item.manifester_id = request.form['manifester_id'] if request.form['manifester_id'] else None
            
            db_session.commit()
            return redirect(url_for('list_lineitem'))
        
        # Get related data for dropdowns
        manifests = db_session.query(Manifest).all()
        packtypes = db_session.query(Packtype).all()
        commoditys = db_session.query(Commodity).all()
        containers = db_session.query(Container).all()
        users = db_session.query(User).all()
        
        return render_template('lineitem/form.html', 
            item=item,
            mode='edit',
            manifests=manifests,
            packtypes=packtypes,
            commoditys=commoditys,
            containers=containers,
            users=users,
        )

    @app.route('/lineitem/<int:id>/delete', methods=['POST'])
    def delete_lineitem(id):
        item = db_session.get(LineItem, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_lineitem'))

    def get_lineitem(offset, limit):
        return db_session.query(LineItem).order_by(
            LineItem.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_lineitem(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(LineItem)\
            .filter(LineItem.description.ilike(search_term))\
            .order_by(LineItem.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()