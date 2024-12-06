
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.container import Container
from generator.output.models.port import Port
import config

def register_container_routes(app):
    @app.route('/container')
    def list_container():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_container(query, offset, config.RECORDS_PER_PAGE) if query else get_container(offset, config.RECORDS_PER_PAGE)
        return render_template('container/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/container/create', methods=['GET', 'POST'])
    def create_container():
        if request.method == 'POST':
            number = request.form['number'] if request.form['number'] else None
            port_id = request.form['port_id'] if request.form['port_id'] else None
            updated = request.form['updated'] if request.form['updated'] else None
            
            new_item = Container(
                number=number,
                port_id=port_id,
                updated=updated,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_container'))
        
        # Get related data for dropdowns
        ports = db_session.query(Port).all()
        
        return render_template('container/form.html', 
            mode='create',
            ports=ports,
        )

    @app.route('/container/<int:id>/edit', methods=['GET', 'POST'])
    def edit_container(id):
        item = db_session.get(Container, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.number = request.form['number'] if request.form['number'] else None
            item.port_id = request.form['port_id'] if request.form['port_id'] else None
            item.updated = request.form['updated'] if request.form['updated'] else None
            
            db_session.commit()
            return redirect(url_for('list_container'))
        
        # Get related data for dropdowns
        ports = db_session.query(Port).all()
        
        return render_template('container/form.html', 
            item=item,
            mode='edit',
            ports=ports,
        )

    @app.route('/container/<int:id>/delete', methods=['POST'])
    def delete_container(id):
        item = db_session.get(Container, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_container'))

    def get_container(offset, limit):
        return db_session.query(Container).order_by(
            Container.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_container(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(Container)\
            .filter(Container.number.ilike(search_term))\
            .order_by(Container.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()