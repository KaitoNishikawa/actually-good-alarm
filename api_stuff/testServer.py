import sys
import os
import json
import math
from datetime import datetime
from flask import Flask, jsonify, request

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
file_number = datetime.now().strftime("%Y%m%d")

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
        absolute_start_time = JSONData.get('absoluteStartTime', None)

        print(f"x length: {len(accelData['x'])}")
        print(f"y length: {len(accelData['y'])}")
        print(f"z length: {len(accelData['z'])}")
        print(f"time length: {len(accelData['timestamp'])}")
        print(f"hr length: {len(HRData['HR'])}")
        print(f"hr time length: {len(HRData['timestamp'])}")

        # file_number = 1214
        file_number_as_str = str(file_number)

        # write data to txt files
        LoadData.write_data_to_files(accelData, HRData, file_number_as_str, absolute_start_time)
        
        # generate features and write to txt files
        runner.run_preprocessing([file_number_as_str])
        # read features into data frame
        data = LoadData.get_features(file_number_as_str)

        if data:
            predictions = Model.run_model(data, file_number_as_str)
            predictions = predictions[-10:]
            print(predictions)
            return jsonify(predictions=predictions.tolist())
        print("not enough data")
        return jsonify(message="not enough data to make prediction"), 500
    
@app.route('/sleep_data', methods=["POST"])
def receive_sleep_data():
    if request.is_json:
        try:
            sleep_data = request.get_json()
            
            # Create a directory for logs if it doesn't exist
            save_dir = 'sleep_data_logs'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Generate a unique filename using the current timestamp
            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # filename = f"{save_dir}/sleep_data_{timestamp}.json"
            filename = f"{save_dir}/sleep_data_{file_number}.json"
            
            # Save the JSON data to the file
            with open(filename, 'w') as f:
                json.dump(sleep_data, f, indent=4)
                
            print(f"Sleep data saved to {filename}")
            return jsonify(message="Sleep data saved successfully"), 200
            
        except Exception as e:
            print(f"Error saving sleep data: {e}")
            return jsonify(message="Internal Server Error"), 500
    else:
        return jsonify(message="Request was not JSON"), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)