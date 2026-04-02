from flask import Flask, render_template, request, redirect, flash
import mysql.connector
import random
import os
from urllib.parse import urlparse
 
app = Flask(__name__)
 
# 🔥 GET DATABASE URL
db_url = os.getenv("DATABASE_URL", "mysql://root:sddliJKjqCmwVkcRQgynyARimBZoMKXO@ballast.proxy.rlwy.net:33489/railway")
url = urlparse(db_url)
 
app.secret_key = "uber_secret_key"

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

# Initialize db at startup
def setup_database():
    db = get_db_connection()
    if db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer (
                name VARCHAR(100) NOT NULL,
                mobile VARCHAR(20) PRIMARY KEY,
                amount DECIMAL(10,2) NOT NULL,
                location VARCHAR(200) NOT NULL
            )
        """)
        db.commit()
        db.close()

setup_database()

# Home Page (READ)
@app.route('/')
def index():
    db = get_db_connection()
    if not db:
        return "Database connection failed!", 500
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customer ORDER BY name ASC")
    data = cursor.fetchall()
    db.close()
    return render_template("index.html", customers=data)

# CREATE
@app.route('/insert', methods=['POST'])
def insert():
    db = get_db_connection()
    if not db:
        return redirect('/')
    
    name = request.form['name']
    mobile = request.form['mobile']
    amount = request.form['amount']
    location = request.form['location']

    cursor = db.cursor()
    try:
        query = "INSERT INTO customer (name, mobile, amount, location) VALUES (%s, %s, %s, %s)"
        values = (name, mobile, amount, location)
        cursor.execute(query, values)
        db.commit()
    except mysql.connector.Error as err:
        print(f"Insert Error: {err}")
    finally:
        db.close()

    return redirect('/')

# DELETE
@app.route('/delete/<mobile>')
def delete(mobile):
    db = get_db_connection()
    if not db:
        return redirect('/')
    
    cursor = db.cursor()
    cursor.execute("DELETE FROM customer WHERE mobile=%s", (mobile,))
    db.commit()
    db.close()
    return redirect('/')

# UPDATE
@app.route('/update', methods=['POST'])
def update():
    db = get_db_connection()
    if not db:
        return redirect('/')
    
    name = request.form['name']
    mobile = request.form['mobile']
    amount = request.form['amount']
    location = request.form['location']

    cursor = db.cursor()
    query = """
    UPDATE customer 
    SET name=%s, amount=%s, location=%s 
    WHERE mobile=%s
    """
    values = (name, amount, location, mobile)

    cursor.execute(query, values)
    db.commit()
    db.close()

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)