
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.containerhistory import ContainerHistory

def register_containerhistory_routes(app):
    @app.route('/containerhistory')
    def list_containerhistory():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_containerhistory(query, offset, config.RECORDS_PER_PAGE) if query else get_containerhistory(offset, config.RECORDS_PER_PAGE)
        return render_template('containerhistory/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/containerhistory/create', methods=['GET', 'POST'])
    def create_containerhistory():
        if request.method == 'POST':
            container_id = request.form['container_id'] if request.form['container_id'] else None
            port_id = request.form['port_id'] if request.form['port_id'] else None
            client_id = request.form['client_id'] if request.form['client_id'] else None
            container_status_id = request.form['container_status_id'] if request.form['container_status_id'] else None
            damage = request.form['damage'] if request.form['damage'] else None
            updated = request.form['updated'] if request.form['updated'] else None
            
            new_item = ContainerHistory(
                container_id=container_id,
                port_id=port_id,
                client_id=client_id,
                container_status_id=container_status_id,
                damage=damage,
                updated=updated,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_containerhistory'))
        
        # Get related data for dropdowns
        containers = db_session.query(Container).all()
        ports = db_session.query(Port).all()
        clients = db_session.query(Client).all()
        containerstatuss = db_session.query(Containerstatus).all()
        
        return render_template('containerhistory/form.html', 
            mode='create',
            containers=containers,
            ports=ports,
            clients=clients,
            containerstatuss=containerstatuss,
        )

    @app.route('/containerhistory/<int:id>/edit', methods=['GET', 'POST'])
    def edit_containerhistory(id):
        item = db_session.get(ContainerHistory, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.container_id = request.form['container_id'] if request.form['container_id'] else None
            item.port_id = request.form['port_id'] if request.form['port_id'] else None
            item.client_id = request.form['client_id'] if request.form['client_id'] else None
            item.container_status_id = request.form['container_status_id'] if request.form['container_status_id'] else None
            item.damage = request.form['damage'] if request.form['damage'] else None
            item.updated = request.form['updated'] if request.form['updated'] else None
            
            db_session.commit()
            return redirect(url_for('list_containerhistory'))
        
        # Get related data for dropdowns
        containers = db_session.query(Container).all()
        ports = db_session.query(Port).all()
        clients = db_session.query(Client).all()
        containerstatuss = db_session.query(Containerstatus).all()
        
        return render_template('containerhistory/form.html', 
            item=item,
            mode='edit',
            containers=containers,
            ports=ports,
            clients=clients,
            containerstatuss=containerstatuss,
        )

    @app.route('/containerhistory/<int:id>/delete', methods=['POST'])
    def delete_containerhistory(id):
        item = db_session.get(ContainerHistory, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_containerhistory'))

    def get_containerhistory(offset, limit):
        return db_session.query(ContainerHistory).order_by(
            ContainerHistory.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_containerhistory(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(ContainerHistory)\
            .filter(ContainerHistory.damage.ilike(search_term))\
            .order_by(ContainerHistory.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()