from plot_data import PlotData
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_stuff.load_data import LoadData
from api_stuff.run_model import Model
from source.preprocessing2.preprocessing_runner import runner

# file_number = datetime.now().strftime("%Y%m%d")
file_number = "20251215"
# print(file_number)


# runner.run_preprocessing([file_number])
# data = LoadData.get_features(file_number)
# print(len(data))
# predictions = Model.run_model(data, file_number)
PlotData.plot_apple_and_model_data_2(file_number)

# date_string = "2025-12-13 09:37:05,988"

# dt_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S,%f")
# timestamp = dt_object.timestamp()

# print(f"Original String: {date_string}")
# print(f"JSON StartTime:  {timestamp}")

# timestamp = 1765730181.2749329
# dt_object = datetime.fromtimestamp(timestamp)
# print(dt_object)