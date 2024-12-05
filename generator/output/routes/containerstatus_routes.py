
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.containerstatus import ContainerStatus

def register_containerstatus_routes(app):
    @app.route('/containerstatus')
    def list_containerstatus():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_containerstatus(query, offset, config.RECORDS_PER_PAGE) if query else get_containerstatus(offset, config.RECORDS_PER_PAGE)
        return render_template('containerstatus/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/containerstatus/create', methods=['GET', 'POST'])
    def create_containerstatus():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            description = request.form['description'] if request.form['description'] else None
            
            new_item = ContainerStatus(
                name=name,
                description=description,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_containerstatus'))
        
        # Get related data for dropdowns
        
        return render_template('containerstatus/form.html', 
            mode='create',
        )

    @app.route('/containerstatus/<int:id>/edit', methods=['GET', 'POST'])
    def edit_containerstatus(id):
        item = db_session.get(ContainerStatus, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.description = request.form['description'] if request.form['description'] else None
            
            db_session.commit()
            return redirect(url_for('list_containerstatus'))
        
        # Get related data for dropdowns
        
        return render_template('containerstatus/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/containerstatus/<int:id>/delete', methods=['POST'])
    def delete_containerstatus(id):
        item = db_session.get(ContainerStatus, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_containerstatus'))

    def get_containerstatus(offset, limit):
        return db_session.query(ContainerStatus).order_by(
            ContainerStatus.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_containerstatus(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(ContainerStatus)\
            .filter(ContainerStatus.name.ilike(search_term))\
            .filter(ContainerStatus.description.ilike(search_term))\
            .order_by(ContainerStatus.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()