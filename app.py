from flask import Flask, render_template, request, jsonify, make_response, json, session
from flask_cors import CORS  # type: ignore
from db import get_db
from models import Person
from dotenv import load_dotenv
import config
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'fallback_secret_key'

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
    limit = config.RECORDS_PER_PAGE
    query = request.args.get('query', '')
    
    if query:
        people = search_people(query, offset, limit)
    else:
        people = get_people(offset, limit)
    
    response = make_response(render_template('table_body.html', people=people))
    if len(people) < limit:
        response.headers['HX-Trigger'] = json.dumps({"noMoreRecords": True})
    return response

def get_people(offset, limit):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM people ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset))
    return [Person(id=row[0], name=row[1], age=row[2]) for row in cursor.fetchall()]

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

        # Add the new person to the session
        if 'new_records' not in session:
            session['new_records'] = []
        session['new_records'].insert(0, new_person.model_dump())  # Insert at the beginning
        session.modified = True
        new_records = [Person(**record) for record in session['new_records']]
        return render_template('table_body.html', people=new_records)
    
    else:
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
    else:
        cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
        row = cursor.fetchone()
        
        if row:
            person = Person(id=row[0], name=row[1], age=row[2])
            return render_template('modal.html', person=person, mode='edit')
        else:
            return "Person not found", 404

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM people WHERE id = ?", (id,))
        db.commit()
        # Return fresh data for the first page
        people = get_people(0, config.RECORDS_PER_PAGE)
        response = make_response(render_template('table_body.html', people=people))
        # Reset the session's new records after delete
        if 'new_records' in session:
            session['new_records'] = []
            session.modified = True
        # Add HX-Trigger to force refresh of the table
        response.headers['HX-Trigger'] = json.dumps({"tableRefreshed": True})
        return response
    except Exception as e:
        db.rollback()
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/refresh_table')
def refresh_table():
    session['new_records'] = [] # Clear the session records
    people = get_people(0, config.RECORDS_PER_PAGE)  # Or however you're fetching initial data
    return render_template('table_body.html', people=people)

@app.route('/get_id/<int:id>')
def get_id(id):
    return str(id)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    people = search_people(query, 0, config.RECORDS_PER_PAGE)
    response = make_response(render_template('table_body.html', people=people)) 
    if len(people) < config.RECORDS_PER_PAGE:
        response.headers['HX-Trigger'] = json.dumps({"noMoreRecords": True})
    return response

def search_people(query, offset, limit):
    db = get_db()
    cursor = db.cursor()
    sql = """
    SELECT * FROM people
    WHERE INSTR(LOWER(name), LOWER(?)) > 0 
        OR INSTR(LOWER(age), LOWER(?)) > 0
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """
    cursor.execute(sql, (query, query, limit, offset))
    results = cursor.fetchall()
    return [Person(id=row[0], name=row[1], age=row[2]) for row in results]

if __name__ == '__main__':
    app.run(debug=True, host=config.HOST, port=config.PORT)
