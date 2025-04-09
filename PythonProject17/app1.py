import sqlite3
import openai
from flask import Flask,request,render_template

openai.api_key='Enter your API key'


app=Flask(__name__)

def init_db():
    con=sqlite3.connect('database.db')
    cursor=con.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_request(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_response TEXT)''')

    con.commit()
    con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    user_input=request.form['user_input']

    con=sqlite3.connect('database.db')
    cursor=con.cursor()
    cursor.execute('INSERT INTO user_request(user_input) VALUES (?)',(user_input,))
    con.commit()
    response=openai.ChatCompletion.create(model='gpt-3.5-turbo',messages=[{'role':'user','content':user_input}])
    ai_response = response['choices'][0]['message']['content']
    cursor.execute('UPDATE user_request SET ai_response=? WHERE user_input=?',(ai_response,user_input))
    con.commit()
    con.close()
    return render_template('index.html',response=ai_response)
@app.route('/view_data')
def view_data():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM user_request")
    data=cursor.fetchall()
    con.close()
    return render_template('view_data.html',data=data)

if __name__=='__main__':
    init_db()
    app.run(debug=True)



