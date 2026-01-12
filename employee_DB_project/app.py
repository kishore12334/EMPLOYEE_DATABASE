# app.py
from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB_PATH = os.path.join("database", "employee.db")
last_deleted = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['user'] = 'admin'
            return redirect('/index')
        return render_template('login.html', error="Invalid Login")
    return render_template('login.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_employee():
    if 'user' not in session:
        return redirect('/')

    data = (
        request.form['emp_name'],
        request.form['gender'],
        request.form['phone'],
        request.form['email'],
        request.form['designation']
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employee (emp_name, gender, phone, email, designation)
        VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    return render_template('success.html')

@app.route('/view')
def view():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM employee")
    employees = cursor.fetchall()
    conn.close()

    return render_template('view.html', employees=employees)

@app.route('/delete/<int:rowid>')
def delete_employee(rowid):
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, * FROM employee WHERE rowid=?", (rowid,))
    row = cursor.fetchone()

    if row:
        last_deleted['data'] = row
        cursor.execute("DELETE FROM employee WHERE rowid=?", (rowid,))
        conn.commit()

    conn.close()
    return redirect('/view?undo=true')

@app.route('/undo')
def undo():
    if 'user' not in session:
        return redirect('/')

    if 'data' in last_deleted:
        row = last_deleted['data']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employee (emp_name, gender, phone, email, designation)
            VALUES (?, ?, ?, ?, ?)
        """, row[2:])
        conn.commit()
        conn.close()
        last_deleted.clear()

    return redirect('/view')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
