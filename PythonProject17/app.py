import hashlib
import sqlite3


import openai
from flask import Flask,request,render_template,flash,redirect,url_for,session


app=Flask(__name__)
app.secret_key='secret'

openai.api_key='your Open AI API key'


app=Flask(__name__)
app.secret_key='secret'

def init_db():
    con=sqlite3.connect('database.db')
    cursor=con.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL)''')
    con.commit()
    con.close()

def init_user_db(username):
    con = sqlite3.connect(f'{username}.db')
    cursor = con.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT,
        ai_response TEXT)''')
    con.commit()
    con.close()

@app.route('/',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        hashed_password=hashlib.sha256(password.encode()).hexdigest()
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        try:
            cursor.execute('INSERT INTO users (username,password) VALUES (?,?)',(username,hashed_password))
            con.commit()
        except sqlite3.IntegrityError:
            cursor.execute('username already exists,please try another one')
        finally:
            cursor.close()
        return redirect(url_for('login'))
    return render_template('signup.html')
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        hashed_password=hashlib.sha256(password.encode()).hexdigest()
        con = sqlite3.connect('database.db')
        cursor = con.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?',(username,hashed_password))
        user=cursor.fetchone()

        if user:
            flash('login successful')

            init_user_db(username)
            return redirect(url_for('index'))
        else:
            flash('invalid credentials,please try again later')
        cursor.close()
    return render_template('login.html')
@app.route('/index',methods=['POST','GET'])
def index():
    return render_template('index.html')
@app.route('/submit',methods=['POST'])
def submit():
    user_input=request.form.get('user_input')
    username=session['username']
    con = sqlite3.connect(f'{username}.db')
    cursor = con.cursor()
    cursor.execute('INSERT INTO user_requests (user_input) VALUES (?)',(user_input,))
    con.commit()


    response=openai.ChatCompletion.create(model='gpt-3.5-turbo',messages=[{"role":'user','content':user_input}],max_tokens=100)
    ai_response=response['choices'][0]['message']['content']
    cursor.execute('UPDATE user_requests SET ai_response=? WHERE user_input=?',(ai_response,user_input))
    con.commit()
    con.close()
    return render_template('index.html',response=ai_response)
@app.route('/view_data')
def view_data():
    username=session['username']
    con = sqlite3.connect(f'{username}.db')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM user_requests')
    data=cursor.fetchall()
    con.close()
    return render_template('view_data.html',data=data)
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully')
    return redirect(url_for('login'))

if __name__=='__main__':
    init_db()
    app.run(debug=True)










