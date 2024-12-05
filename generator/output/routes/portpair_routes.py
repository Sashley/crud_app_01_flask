
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.portpair import PortPair

def register_portpair_routes(app):
    @app.route('/portpair')
    def list_portpair():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_portpair(query, offset, config.RECORDS_PER_PAGE) if query else get_portpair(offset, config.RECORDS_PER_PAGE)
        return render_template('portpair/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/portpair/create', methods=['GET', 'POST'])
    def create_portpair():
        if request.method == 'POST':
            pol_id = request.form['pol_id'] if request.form['pol_id'] else None
            pod_id = request.form['pod_id'] if request.form['pod_id'] else None
            distance = int(request.form['distance']) if request.form['distance'] else None
            
            new_item = PortPair(
                pol_id=pol_id,
                pod_id=pod_id,
                distance=distance,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_portpair'))
        
        # Get related data for dropdowns
        ports = db_session.query(Port).all()
        ports = db_session.query(Port).all()
        
        return render_template('portpair/form.html', 
            mode='create',
            ports=ports,
            ports=ports,
        )

    @app.route('/portpair/<int:id>/edit', methods=['GET', 'POST'])
    def edit_portpair(id):
        item = db_session.get(PortPair, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.pol_id = request.form['pol_id'] if request.form['pol_id'] else None
            item.pod_id = request.form['pod_id'] if request.form['pod_id'] else None
            item.distance = int(request.form['distance']) if request.form['distance'] else None
            
            db_session.commit()
            return redirect(url_for('list_portpair'))
        
        # Get related data for dropdowns
        ports = db_session.query(Port).all()
        ports = db_session.query(Port).all()
        
        return render_template('portpair/form.html', 
            item=item,
            mode='edit',
            ports=ports,
            ports=ports,
        )

    @app.route('/portpair/<int:id>/delete', methods=['POST'])
    def delete_portpair(id):
        item = db_session.get(PortPair, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_portpair'))

    def get_portpair(offset, limit):
        return db_session.query(PortPair).order_by(
            PortPair.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_portpair(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(PortPair)\
            .order_by(PortPair.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()