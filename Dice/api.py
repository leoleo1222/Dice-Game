from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# Define the path to the CSV file
csv_file = 'sum_records.csv'


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


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
