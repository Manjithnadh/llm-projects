from flask import Flask, render_template, request, jsonify
import sqlite3
import openai

app = Flask(__name__)

# Configure OpenAI API Key
openai.api_key = 'your Open API key'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Route to display the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle user input and AI response
@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']

    # Store user input in the database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_requests (user_input) VALUES (?)", (user_input,))
    conn.commit()

    # Query the OpenAI API for AI response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Updated model for chat-based requests
        messages=[
            {"role": "user", "content": user_input}  # Format the input as a message
        ]
    )

    # Get the AI's response
    ai_response = response['choices'][0]['message']['content']

    # Store the AI response in the database
    cursor.execute("UPDATE user_requests SET ai_response = ? WHERE user_input = ?", (ai_response, user_input))
    conn.commit()
    conn.close()

    return render_template('index.html', response=ai_response)

# Route to view stored data
@app.route('/view_data')
def view_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_requests")
    data = cursor.fetchall()
    conn.close()
    return render_template('view_data.html', data=data)

if __name__ == '__main__':
    init_db()  # Initialize the database when the app starts
    app.run(debug=True)
