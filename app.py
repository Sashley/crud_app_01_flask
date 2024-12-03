from flask import Flask, render_template, request, jsonify, make_response, json, session, url_for
from flask_cors import CORS  # type: ignore
from db import get_db
from models import Person
from dotenv import load_dotenv
import config
import os

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

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
        age = request.form['age']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO people (name, age) VALUES (?, ?)", (name, age))
        db.commit()
        new_id = cursor.lastrowid
        new_person = Person(id=new_id, name=name, age=age)

        if 'new_records' not in session:
            session['new_records'] = []
        session['new_records'].insert(0, new_person.model_dump())
        session.modified = True
        new_records = [Person(**record) for record in session['new_records']]
        return render_template('table_body.html', people=new_records)
    
    return render_template('modal.html', person=Person(id=0, name='', age=0), mode='create')

@app.route('/edit/<int:id>', methods=['GET', 'POST', 'PUT'])
def edit(id):
    db = get_db()
    cursor = db.cursor()

    if request.method in ['POST', 'PUT']:
        name = request.form['name']
        age = request.form['age']
        cursor.execute("UPDATE people SET name = ?, age = ? WHERE id = ?", (name, age, id))
        db.commit()
        cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
        row = cursor.fetchone()
        updated_person = Person(id=row[0], name=row[1], age=row[2])
        return render_template('person_row.html', person=updated_person)
    
    cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        person = Person(id=row[0], name=row[1], age=row[2])
        return render_template('modal.html', person=person, mode='edit')
    return "Person not found", 404

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM people WHERE id = ?", (id,))
        db.commit()
        people = get_people(0, config.RECORDS_PER_PAGE)
        response = make_response(render_template('table_body.html', people=people))
        if 'new_records' in session:
            session['new_records'] = []
            session.modified = True
        response.headers['HX-Trigger'] = json.dumps({"tableRefreshed": True})
        return response
    except Exception as e:
        db.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/get_id/<int:id>')
def get_id(id):
    return str(id)

# Helper functions
def get_people(offset, limit):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM people ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    return [Person(id=row[0], name=row[1], age=row[2]) for row in cursor.fetchall()]

def search_people(query, offset, limit):
    db = get_db()
    cursor = db.cursor()
    sql = """
    SELECT * FROM people
    WHERE LOWER(name) LIKE LOWER(?) OR CAST(age AS TEXT) LIKE ?
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """
    search_term = f"%{query}%"
    cursor.execute(sql, (search_term, search_term, limit, offset))
    return [Person(id=row[0], name=row[1], age=row[2]) for row in cursor.fetchall()]

if __name__ == '__main__':
    app.run(debug=True, host=config.HOST, port=config.PORT)
