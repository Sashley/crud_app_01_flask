from flask import Flask, render_template, request, jsonify, session, make_response, json # type: ignore
from flask_cors import CORS # type: ignore
from db import get_db
from models import Person
import config

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'  # Set a secret key for sessions

from db import get_db
from models import Person
import config
import json

app = Flask(__name__)

@app.route('/')
def index():
    initial_people = get_people(0, config.RECORDS_PER_PAGE)
    return render_template('index.html', 
        people=initial_people, 
        records_per_page=config.RECORDS_PER_PAGE)

@app.route('/load_more')
def load_more():
    offset = int(request.args.get('offset', 0))
    limit = config.RECORDS_PER_PAGE
    print(f"Load More - Offset: {offset}, Limit: {limit}")
    people = get_people(offset, limit)
    print(f"Fetched {len(people)} records")
    
    response = make_response(render_template('table_body.html', people=people))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    if len(people) < limit:
        print("No more records")
        response.headers['HX-Trigger'] = json.dumps({"noMoreRecords": True})
    
    return response

def get_people(offset, limit):
    db = get_db()
    cursor = db.cursor()
    print(f"Fetching {limit} records starting from {offset}")
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
        session['new_records'].insert(0, new_person.dict())  # Insert at the beginning
        session.modified = True

        # Fetch all new records
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
        
        # Fetch all people to update the table
        cursor.execute("SELECT * FROM people ORDER BY id DESC")
        people = [Person(id=row[0], name=row[1], age=row[2]) for row in cursor.fetchall()]
        return render_template('table_body.html', people=people)
    else:
        cursor.execute("SELECT * FROM people WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            person = Person(id=row[0], name=row[1], age=row[2])
            print("person: ", person)
            return render_template('modal.html', person=person, mode='edit')
        else:
            return "Person not found", 404

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM people WHERE id = ?", (id,))
    db.commit()

    # Fetch all remaining people
    cursor.execute("SELECT * FROM people ORDER BY id DESC")
    people = [Person(id=row[0], name=row[1], age=row[2]) for row in cursor.fetchall()]
    
    # Render the updated table body
    return render_template('table_body.html', people=people)

@app.route('/get_id/<int:id>')
def get_id(id):
    return str(id)

if __name__ == '__main__':
    app.run(debug=True, host=config.HOST, port=config.PORT)