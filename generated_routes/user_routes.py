
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.user import User

bp = Blueprint('user', __name__)

def register_user_routes(app):
    app.register_blueprint(bp)

@bp.route('/user')
def list_user():
    query = User.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        filters.append(User.name.ilike(f'%{search}%'))
        filters.append(User.email.ilike(f'%{search}%'))
        filters.append(User.password_hash.ilike(f'%{search}%'))
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '-id')
    if sort.startswith('-'):
        query = query.order_by(getattr(User, sort[1:]).desc())
    else:
        query = query.order_by(getattr(User, sort))
    
    items = query.all()
    return render_template(
        'user/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/user/new', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        item = User()
        item.name = request.form.get('name')
        item.email = request.form.get('email')
        item.password_hash = request.form.get('password_hash')
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('user.list_user'))
    
    return render_template('user/form.html')

@bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    item = User.query.get_or_404(id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.email = request.form.get('email')
        item.password_hash = request.form.get('password_hash')
        
        db_session.commit()
        return redirect(url_for('user.list_user'))
    
    return render_template('user/form.html', item=item)

@bp.route('/user/<int:id>/delete', methods=['POST'])
def delete_user(id):
    item = User.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('user.list_user'))