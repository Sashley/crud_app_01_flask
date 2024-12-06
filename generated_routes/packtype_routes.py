
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.packtype import PackType

bp = Blueprint('packtype', __name__)

def register_packtype_routes(app):
    app.register_blueprint(bp)

@bp.route('/packtype')
def list_packtype():
    query = PackType.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(PackType.name.ilike(f'%{search}%'))
        filters.append(PackType.description.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(PackType, sort[1:]).desc())
    else:
        query = query.order_by(getattr(PackType, sort))
    
    items = query.all()
    return render_template(
        'packtype/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/packtype/new', methods=['GET', 'POST'])
def create_packtype():
    if request.method == 'POST':
        item = PackType()
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('packtype.list_packtype'))
    
    return render_template('packtype/form.html')

@bp.route('/packtype/<int:id>/edit', methods=['GET', 'POST'])
def edit_packtype(id):
    item = PackType.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        
        db_session.commit()
        return redirect(url_for('packtype.list_packtype'))
    
    return render_template('packtype/form.html', item=item)

@bp.route('/packtype/<int:id>/delete', methods=['POST'])
def delete_packtype(id):
    item = PackType.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('packtype.list_packtype'))