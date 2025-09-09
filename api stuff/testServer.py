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

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    runner.run_preprocessing(["46343"])
    return jsonify(message='Hello World')

@app.route('/data', methods=["POST"])
def receive():
    if request.is_json:
        JSONData = request.get_json()

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

        file_number = 11
        file_number_as_str = str(file_number)

        # write data to txt files
        LoadData.write_data_to_files(accelData, HRData, file_number_as_str)
        
        # generate features and write to txt files
        runner.run_preprocessing([file_number_as_str])
        # read features into data frame
        data = LoadData.get_features(file_number_as_str)

        if data:
            predictions = Model.run_model(data, file_number_as_str)
            print(predictions)
            return jsonify(predictions=predictions.tolist())
        print("not enough data")
        return jsonify(message="not enough data to make prediction"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)