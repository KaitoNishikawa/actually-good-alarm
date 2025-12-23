import sys
import os
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from api_stuff.load_data import LoadData
from api_stuff.run_model import Model

from source.preprocessing2.preprocessing_runner import runner

# file_number = datetime.now().strftime("%Y%m%d")
# print(file_number)

file_numbers = ['20251213', '20251214', '20251215', '20251217', '20251219', '20251221', '20251222']

for file_number in file_numbers:
    runner.run_preprocessing([file_number])
    data = LoadData.get_features(file_number)
    print(len(data))
    predictions = Model.run_model(data, file_number)
