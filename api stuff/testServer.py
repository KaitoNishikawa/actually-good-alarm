import sys
import os
import json
import math

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request

from source.preprocessing2.preprocessing_runner import runner
from load_data import LoadData
from run_model import Model

# runner.run_preprocessing(["3"])

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    runner.run_preprocessing(["46343"])
    return jsonify(message='Hello from your test API!')

@app.route('/test', methods=["POST"])
def receive():
    if request.is_json:
        JSONData = request.get_json()
        # print(JSONData)
        # print(JSONData["accel_timestamp"])
        # print(JSONData["heartRate_timestamp"])
        accelData = {
            'x': JSONData['x'],
            'y': JSONData['y'],
            'z': JSONData['z'],
            'timestamp': JSONData['accel_timestamp']
        }
        HRData = {
            'HR': JSONData['heartRate'],
            'timestamp': JSONData['heartRate_timestamp']
        }
        print(f'x length: {len(accelData['x'])}')
        print(f'y length: {len(accelData['y'])}')
        print(f'z length: {len(accelData['z'])}')
        print(f'time length: {len(accelData['timestamp'])}')
        print(f'hr length: {len(HRData['HR'])}')
        print(f'time length: {len(HRData['timestamp'])}')
        # parsedData = json.loads(JSONData)
        # print(f'x: {parsedData["x"]}')
        # print(f'time: {parsedData["accel_timestamp"]}')

        with open('data/motion/6_acceleration.txt', 'a') as file:
            for index, i in enumerate(accelData['timestamp']):
                newLine = str(i) + ' ' + str(accelData['x'][index]) + ' ' + str(accelData['y'][index]) + ' ' + str(accelData['z'][index]) + '\n'
                file.write(newLine)

        with open('data/heart_rate/6_heartrate.txt', 'a') as file:
            for index, i in enumerate(HRData['timestamp']):
                newLine = str(i) + ',' + str(HRData['HR'][index]) + '\n'
                file.write(newLine)
        with open('data/labels/6_labeled_sleep.txt', 'w') as file:
            iteration_amount = math.floor(accelData['timestamp'][-1] / 30) + 1

            for i in range(iteration_amount):
                newLine = str(i * 30) + ' ' + '0' + '\n'
                file.write(newLine)

        
        runner.run_preprocessing(["6"])
        data = LoadData.get_features()

        if data:
            predictions = Model.run_model(data)
            print(predictions)
            return jsonify(predictions=predictions.tolist())
        print("not enough data")
        return jsonify(message="not enough data to make prediction"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)