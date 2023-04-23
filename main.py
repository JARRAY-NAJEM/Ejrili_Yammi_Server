import psycopg2
from flask import Flask, jsonify, request, send_file
from psycopg2 import connect, extras
from cryptography.fernet import Fernet
from os import environ
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template
from flask import Flask, render_template, url_for, request, jsonify
import requests
import os
load_dotenv()
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
key = Fernet.generate_key()


host = environ.get('DB_HOST')
database = environ.get('DB_NAME')
username = environ.get('DB_USER')
password = environ.get('DB_PASSWORD')
port = environ.get('DB_PORT')

# Auth database postgresql


def get_db_connection():
    conn = connect(host='localhost',
                   database='postgres',
                   user='postgres',
                   password='password',
                   port=5432)
  #  conn.set_isolation_level(0)
#    DATABASE_URI = 'postgres://postgres_ejrili:bCHICAykURsRLPLI8evkHsWW7Js5ggQI@dpg-ch2kk9dgk4qarqhhjsh0-a.oregon-postgres.render.com/postgres_ejrili'

    # conn = psycopg2.connect(DATABASE_URI)

    return conn
@app.route('/chat', methods=['POST'])


def send_from_user():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({"error": "Invalid Input"})

        response = send_to_rasa(message)
        return jsonify(response)
    
    except requests.exceptions.RequestException as e:
         return jsonify({"error": f"Failed to connect to Rasa server: {e}"})


def send_to_rasa(message):
    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
    data = {'message': message}
    try:
        response = requests.post(rasa_url, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to communicate with Rasa server."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to Rasa server: {e}"}


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute("SELECT * FROM account_user")

    users = cur.fetchall()

    for user in users:
        if user['email'] == email and user['password'] == password:
            return jsonify({'message': 'Login Successful. '}),  200

    return jsonify({'message': 'Email Not already exists in the database. '}), 400
# add user


@app.post('/api/postAccount')
def create_user():
    new_user = request.get_json()
    firstname = new_user['firstname']
    name = new_user['name']
    username = new_user['username']
    email = new_user['email']
    # for cryptage password
    # password = Fernet(key).encrypt(bytes(new_user['password'], 'utf-8'))
    password = new_user['password']
    phone = new_user['phone']
    gradient = new_user['gradient']
    relationship = new_user['relationship']
    contact1 = new_user['contact1']
    contact2 = new_user['contact2']
    information = new_user['information']
    medications = new_user['medications']
    allergies = new_user['allergies']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:

        cur.execute("INSERT INTO account_user (firstname,name,username,email,phone,password,gradient,relationship,contact1,contact2,information,medications,allergies) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
                    (firstname, name, username, email, phone, password, gradient, relationship, contact1, contact2, information, medications, allergies))
        new_user = cur.fetchone()
        conn.commit()
        response = new_user
        status_code = 200
    except psycopg2.IntegrityError:
        conn.rollback()
        response = {"message": "Email already exists in the database."}
        status_code = 500
    finally:
        cur.close()
        conn.close()
    # print(new_user)

    return jsonify(response), status_code

# get all users


@app.route('/api/get', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        query = "SELECT * FROM account_user"
        cur.execute(query)
        users = cur.fetchall()
        cur.close()
        conn.close()

        if not users:
            return jsonify({'message': 'No users found'}), 404

        return jsonify(users)

    except Exception as e:
        return jsonify({'message': str(e)}), 500



@app.route('/api/getUser/<email>', methods=['GET'])
def get_one_user(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        query = "SELECT * FROM account_user WHERE email = %s"
        cur.execute(query, (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify(user)

    except Exception as e:
        return jsonify({'message': str(e)}), 500



# add user
# @app.post('/api/post')
# def create_user():
#    new_user = request.get_json()
#    username = new_user['username']
#    email = new_user['email']
#    # password = Fernet(key).encrypt(bytes(new_user['password'], 'utf-8'))
#    password = new_user['password']
#
#    conn = get_db_connection()
#    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
#    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING *",
#                (username, email, password))
#    new_user = cur.fetchone()
#    conn.commit()
#    cur.close()
#    conn.close()
#
#    return jsonify(new_user)


# get only user by Email and password
@app.route('/api/get/<email>/<password>', methods=['GET'])
def get_user(email, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        query = "SELECT * FROM account_user WHERE email = %s AND password = %s"
        cur.execute(query, (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user is None:
            return jsonify({'message': 'User not found'}), 404

        return jsonify(user), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500


# update user by id
@app.route('/api/put/<string:email>', methods=['PUT'])
def update_user(email):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        updated_user = request.get_json()
        cur.execute(
            "UPDATE account_user SET firstname=%s,name=%s,username=%s,email=%s,phone=%s,password=%s,gradient=%s,relationship=%s,contact1=%s,contact2=%s,information=%s,medications=%s,allergies=%s WHERE email = %s RETURNING *",
            (updated_user['firstname'], updated_user['name'], updated_user['username'], updated_user['email'], updated_user['phone'], updated_user['password'], updated_user['gradient'], updated_user['relationship'], updated_user['contact1'], updated_user['contact2'], updated_user['information'], updated_user['medications'], updated_user['allergies'], email)
        )
        updated_user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if updated_user is None:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'message': 'update success'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# delete user by id
# @app.delete('/api/del/<from>')
# def delete_user(id):
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=extras.RealDictCursor)
#     cur.execute("DELETE FROM account_user WHERE id = %s RETURNING *", (id,))
#     user = cur.fetchone()
#     conn.commit()
#     cur.close()
#     conn.close()
#     if user is None:
#         return jsonify({'message': 'User not found'}), 404
#     return jsonify(user)

# first return sync running server "homePage"


@app.route('/', methods=['GET'])

def home():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    sql = '''CREATE TABLE IF NOT EXISTS account_user (
        id SERIAL PRIMARY KEY NOT NULL ,
        firstname VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        phone VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        gradient VARCHAR(255) ,
        relationship VARCHAR(255) ,
        contact1 VARCHAR(255) ,
        contact2 VARCHAR(255) ,
        information VARCHAR(2555) ,
        medications  VARCHAR(2555)  ,
        allergies  VARCHAR(2555)  ,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );'''
    # print(sql)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

    return jsonify('Ejrili Rasa Server Application')



# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run()
#     # app.run()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# from flask import Flask, render_template, url_for, request, jsonify
# import requests

# app = Flask(__name__)
# @app.route('/webhook', methods=['POST'])
# def send_from_user():
#     try:
#         message = request.json.get('message')
#         if not message:
#             return jsonify({"error": "Invalid Input"})

#         response = send_to_rasa(message)
#         return jsonify(response)
    
#     except requests.exceptions.RequestException as e:
#          return jsonify({"error": f"Failed to connect to Rasa server: {e}"})


# def send_to_rasa(message):
#     rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
#     data = {'message': message}
#     try:
#         response = requests.post(rasa_url, json=data)
#         response.raise_for_status()
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": "Failed to communicate with Rasa server."}
#     except requests.exceptions.RequestException as e:
#         return {"error": f"Failed to connect to Rasa server: {e}"}

# if __name__ == "__main__":
#     app.run(debug=True, port=3000)
# from flask import Flask, render_template, url_for, request, jsonify
# import requests

# app = Flask(__name__)

# # Define the route for incoming messages
# @app.route('/chat', methods=['POST'])

# def send_from_user():
#     try:
#         message = request.json.get('message')
#         if not message:
#             return jsonify({"error": "Invalid Input"})

#         response = send_to_rasa(message)
#         return jsonify(response)
    
#     except requests.exceptions.RequestException as e:
#          return jsonify({"error": f"Failed to connect to Rasa server: {e}"})


# def send_to_rasa(message):
#     rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
#     data = {'message': message}
#     try:
#         response = requests.post(rasa_url, json=data)
#         response.raise_for_status()
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": "Failed to communicate with Rasa server."}
#     except requests.exceptions.RequestException as e:
#         return {"error": f"Failed to connect to Rasa server: {e}"}

# if __name__ == '__main__':
#     app.run(debug=True,port=5000)


