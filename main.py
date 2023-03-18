from flask import Flask, jsonify, request, send_file
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from os import environ
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
key = Fernet.generate_key()

host = environ.get('DB_HOST')
database = environ.get('DB_NAME')
username = environ.get('DB_USER')
password = environ.get('DB_PASSWORD')
port = environ.get('DB_PORT')


# Auth database postgres
def get_db_connection():
    conn = connect(host='localhost',
                   database='postgres',
                   user='postgres',
                   password='password',
                   port=5432
                   )
    return conn

# get all users
@app.get('/api/get')
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)

# add user
@app.post('/api/post')
def create_user():
    new_user = request.get_json()
    username = new_user['username']
    email = new_user['email']
    # password = Fernet(key).encrypt(bytes(new_user['password'], 'utf-8'))
    password = new_user['password']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING *",
                (username, email, password))
    new_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(new_user)


# get only user by id
@app.get('/api/get/<id>')
def get_user(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user)

# update user by id
@app.put('/api/put/<id>')
def update_user(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    new_user = request.get_json()
    username = new_user['username']
    email = new_user['email']
    # password = Fernet(key).encrypt(bytes(new_user['password'], 'utf-8'))
    password = new_user['password']

    cur.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s RETURNING *",
                (username, email, password, id))
    updated_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated_user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(updated_user)

# delete user by id
@app.delete('/api/del/<id>')
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("DELETE FROM users WHERE id = %s RETURNING *", (id,))
    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user)

# first return sync running server "homePage"
@app.get('/')
def home():
    return 'asma is the best graphic design in societe NjmTech '


if __name__ == '__main__':
    print("flask server running 3000")


    app.run(debug=True, port=3000)
