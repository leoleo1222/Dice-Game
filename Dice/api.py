from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Define the path to the CSV file
csv_file = 'sum_records.csv'

# Define the path to the CSV file
account_file = 'account.csv'


@app.route('/game', methods=['GET'])
def game():
    return render_template("game.html")


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    hashed_password = generate_password_hash(password)

    if os.path.exists(account_file):
        df = pd.read_csv(account_file)
        # Check if the username already exists
        if df[df['username'] == username].shape[0] > 0:
            return jsonify({'message': 'Username already exists'}), 400
        # If the username doesn't exist, append the new account
        df = df._append({'username': username, 'password': hashed_password, 'amount': 100}, ignore_index=True)
    else:
        # If the file doesn't exist, create a new DataFrame
        df = pd.DataFrame({'username': [username], 'password': [hashed_password], 'amount': [100]})
    df.to_csv(account_file, index=False)
    return jsonify({'message': 'Account created successfully'}), 200


@app.route('/add_amount', methods=['POST'])
def add_amount():
    data = request.get_json(force=True)

    username = data.get('username')
    amount = data.get('amount')

    if os.path.exists(account_file):
        df = pd.read_csv(account_file)
        # Check if the username exists
        if df[df['username'] == username].shape[0] > 0:
            # Add the amount to the user's account
            df.loc[df['username'] == username, 'amount'] += amount
        else:
            return jsonify({'message': 'Username does not exist'}), 400
    else:
        return jsonify({'message': 'No users registered'}), 400

    df.to_csv(account_file, index=False)
    return jsonify({'message': 'Amount added successfully'}), 200


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    if os.path.exists(account_file):
        df = pd.read_csv(account_file)
        user = df[df['username'] == username].iloc[0]

        if user is not None and check_password_hash(user['password'], password):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    else:
        return jsonify({'message': 'No users registered'}), 401


@app.route('/save', methods=['POST'])
def save_sum():
    sum_value = int(request.json['sum'])  # Ensure sum_value is an integer
    if os.path.exists(csv_file):
        # If the file exists, append the new sum
        df = pd.read_csv(csv_file)
        df = df._append({'Sum': sum_value}, ignore_index=True)
    else:
        # If the file doesn't exist, create a new DataFrame
        df = pd.DataFrame({'Sum': [sum_value]})
    df.to_csv(csv_file, index=False)
    return jsonify({'message': 'Sum saved successfully'}), 200


@app.route('/get', methods=['GET'])
def get_record():
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Get the last 10 records
        data = df.tail(10).iloc[::-1].to_dict('records')
    else:
        data = []
    return jsonify(data), 200


@app.route('/percentage', methods=['GET'])
def get_percentage():
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        data = []

        # Calculate the occurrence of each number
        counts = df['Sum'].value_counts().to_dict()

        # Calculate the proportion of each number
        total = df['Sum'].count()
        proportions = {k: v / total for k, v in counts.items()}

        # Add the counts and proportions to the data
        data.append({'proportions': proportions})
    else:
        data = []
    return jsonify(data), 200


@app.route('/bigsmall', methods=['GET'])
def get_bigsmall():
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        data = []

        # Create a new column for "Big" and "Small"
        df['Type'] = df['Sum'].apply(lambda x: 'Big' if x >= 11 else 'Small')

        # Calculate the occurrence of each type
        counts = df['Type'].value_counts().to_dict()

        # Calculate the proportion of each type
        total = df['Type'].count()
        proportions = {k: v / total for k, v in counts.items()}

        # Add the counts and proportions to the data
        data.append({'proportions': proportions})
    else:
        data = []
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5500)
