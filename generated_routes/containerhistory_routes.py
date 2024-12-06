
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.containerhistory import ContainerHistory

bp = Blueprint('containerhistory', __name__)

def register_containerhistory_routes(app):
    app.register_blueprint(bp)

@bp.route('/containerhistory')
def list_containerhistory():
    query = ContainerHistory.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(ContainerHistory.damage.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(ContainerHistory, sort[1:]).desc())
    else:
        query = query.order_by(getattr(ContainerHistory, sort))
    
    items = query.all()
    return render_template(
        'containerhistory/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/containerhistory/new', methods=['GET', 'POST'])
def create_containerhistory():
    if request.method == 'POST':
        item = ContainerHistory()
        item.container_id = request.form.get('container_id')
        item.port_id = request.form.get('port_id')
        item.client_id = request.form.get('client_id')
        item.container_status_id = request.form.get('container_status_id')
        item.damage = request.form.get('damage')
        item.updated = request.form.get('updated')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('containerhistory.list_containerhistory'))
    
    return render_template('containerhistory/form.html')

@bp.route('/containerhistory/<int:id>/edit', methods=['GET', 'POST'])
def edit_containerhistory(id):
    item = ContainerHistory.query.get_or_404(id)
    
    if request.method == 'POST':
        item.container_id = request.form.get('container_id')
        item.port_id = request.form.get('port_id')
        item.client_id = request.form.get('client_id')
        item.container_status_id = request.form.get('container_status_id')
        item.damage = request.form.get('damage')
        item.updated = request.form.get('updated')
        
        db_session.commit()
        return redirect(url_for('containerhistory.list_containerhistory'))
    
    return render_template('containerhistory/form.html', item=item)

@bp.route('/containerhistory/<int:id>/delete', methods=['POST'])
def delete_containerhistory(id):
    item = ContainerHistory.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('containerhistory.list_containerhistory'))