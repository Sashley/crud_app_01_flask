
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.user import User
import config

def register_user_routes(app):
    @app.route('/user')
    def list_user():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_user(query, offset, config.RECORDS_PER_PAGE) if query else get_user(offset, config.RECORDS_PER_PAGE)
        return render_template('user/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/user/create', methods=['GET', 'POST'])
    def create_user():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            email = request.form['email'] if request.form['email'] else None
            password_hash = request.form['password_hash'] if request.form['password_hash'] else None
            
            new_item = User(
                name=name,
                email=email,
                password_hash=password_hash,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_user'))
        
        # Get related data for dropdowns
        
        return render_template('user/form.html', 
            mode='create',
        )

    @app.route('/user/<int:id>/edit', methods=['GET', 'POST'])
    def edit_user(id):
        item = db_session.get(User, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.email = request.form['email'] if request.form['email'] else None
            item.password_hash = request.form['password_hash'] if request.form['password_hash'] else None
            
            db_session.commit()
            return redirect(url_for('list_user'))
        
        # Get related data for dropdowns
        
        return render_template('user/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/user/<int:id>/delete', methods=['POST'])
    def delete_user(id):
        item = db_session.get(User, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_user'))

    def get_user(offset, limit):
        return db_session.query(User).order_by(
            User.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_user(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(User)\
            .filter(User.name.ilike(search_term))\
            .filter(User.email.ilike(search_term))\
            .filter(User.password_hash.ilike(search_term))\
            .order_by(User.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()