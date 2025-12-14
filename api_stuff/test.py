from plot_data import PlotData
from load_data import LoadData
from run_model import Model
from datetime import datetime

file_number = datetime.now().strftime("%Y%m%d")
print(file_number)
# PlotData.plot_apple_and_model_data_2(file_number)

# data = LoadData.get_features(file_number)
# print(len(data))
# predictions = Model.run_model(data, file_number)

# date_string = "2025-12-13 09:37:05,988"

# dt_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S,%f")
# timestamp = dt_object.timestamp()

# print(f"Original String: {date_string}")
# print(f"JSON StartTime:  {timestamp}")