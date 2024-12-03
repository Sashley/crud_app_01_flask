from flask import Flask, render_template, request, jsonify, make_response, json, session
from flask_cors import CORS
from models import Person
from database import db_session, init_db, shutdown_session
from sqlalchemy import String
from dotenv import load_dotenv
import config
import os

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

@app.teardown_appcontext
def shutdown_session_handler(exception=None):
    shutdown_session()

# Main routes
@app.route('/')
def index():
    initial_people = get_people(0, config.RECORDS_PER_PAGE)
    return render_template('index.html', 
        people=initial_people, 
        records_per_page=config.RECORDS_PER_PAGE
    )

@app.route('/load_more')
def load_more():
    offset = int(request.args.get('offset', 0))
    query = request.args.get('query', '')
    
    people = search_people(query, offset, config.RECORDS_PER_PAGE) if query else get_people(offset, config.RECORDS_PER_PAGE)
    
    response = make_response(render_template('table_body.html', people=people))
    if len(people) < config.RECORDS_PER_PAGE:
        response.headers['HX-Trigger'] = json.dumps({"noMoreRecords": True})
    return response

@app.route('/search')
def search():
    query = request.args.get('query', '')
    people = search_people(query, 0, config.RECORDS_PER_PAGE)
    response = make_response(render_template('table_body.html', people=people))
    if len(people) < config.RECORDS_PER_PAGE:
        response.headers['HX-Trigger'] = json.dumps({"noMoreRecords": True})
    return response

# CRUD operations
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        new_person = Person(name=name, age=age)
        db_session.add(new_person)
        db_session.commit()

        if 'new_records' not in session:
            session['new_records'] = []
        session['new_records'].insert(0, new_person.to_dict())
        session.modified = True
        new_records = [Person(**record) for record in session['new_records']]
        return render_template('table_body.html', people=new_records)
    
    return render_template('modal.html', person=Person(name='', age=0), mode='create')

@app.route('/edit/<int:id>', methods=['GET', 'POST', 'PUT'])
def edit(id):
    if request.method in ['POST', 'PUT']:
        person = db_session.get(Person, id)
        if person:
            person.name = request.form['name']
            person.age = int(request.form['age'])
            db_session.commit()
            return render_template('person_row.html', person=person)
        return "Person not found", 404
    
    person = db_session.get(Person, id)
    if person:
        return render_template('modal.html', person=person, mode='edit')
    return "Person not found", 404

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        person = db_session.get(Person, id)
        if person:
            db_session.delete(person)
            db_session.commit()
            people = get_people(0, config.RECORDS_PER_PAGE)
            response = make_response(render_template('table_body.html', people=people))
            if 'new_records' in session:
                session['new_records'] = []
                session.modified = True
            response.headers['HX-Trigger'] = json.dumps({"tableRefreshed": True})
            return response
        return "Person not found", 404
    except Exception as e:
        db_session.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/get_id/<int:id>')
def get_id(id):
    return str(id)

# Helper functions
def get_people(offset, limit):
    return db_session.query(Person).order_by(Person.id.desc()).offset(offset).limit(limit).all()

def search_people(query, offset, limit):
    search_term = f"%{query}%"
    return db_session.query(Person)\
        .filter((Person.name.ilike(search_term)) | (Person.age.cast(String).ilike(search_term)))\
        .order_by(Person.id.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host=config.HOST, port=config.PORT)
