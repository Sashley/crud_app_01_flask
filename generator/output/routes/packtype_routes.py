
from flask import request, render_template, redirect, url_for
from database import db_session
from generator.output.models.packtype import PackType

def register_packtype_routes(app):
    @app.route('/packtype')
    def list_packtype():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_packtype(query, offset, config.RECORDS_PER_PAGE) if query else get_packtype(offset, config.RECORDS_PER_PAGE)
        return render_template('packtype/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/packtype/create', methods=['GET', 'POST'])
    def create_packtype():
        if request.method == 'POST':
            name = request.form['name'] if request.form['name'] else None
            description = request.form['description'] if request.form['description'] else None
            
            new_item = PackType(
                name=name,
                description=description,
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_packtype'))
        
        # Get related data for dropdowns
        
        return render_template('packtype/form.html', 
            mode='create',
        )

    @app.route('/packtype/<int:id>/edit', methods=['GET', 'POST'])
    def edit_packtype(id):
        item = db_session.get(PackType, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            item.name = request.form['name'] if request.form['name'] else None
            item.description = request.form['description'] if request.form['description'] else None
            
            db_session.commit()
            return redirect(url_for('list_packtype'))
        
        # Get related data for dropdowns
        
        return render_template('packtype/form.html', 
            item=item,
            mode='edit',
        )

    @app.route('/packtype/<int:id>/delete', methods=['POST'])
    def delete_packtype(id):
        item = db_session.get(PackType, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_packtype'))

    def get_packtype(offset, limit):
        return db_session.query(PackType).order_by(
            PackType.id.desc(),
        ).offset(offset).limit(limit).all()

    def search_packtype(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query(PackType)\
            .filter(PackType.name.ilike(search_term))\
            .filter(PackType.description.ilike(search_term))\
            .order_by(PackType.id.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()