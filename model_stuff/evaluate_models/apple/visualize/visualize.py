import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
sys.path.insert(0, project_root)

from model_stuff.evaluate_models.apple.visualize.plot_data import PlotData

# file_numbers = ['20251213', '20251214', '20251215', '20251217', '20251219', '20251221', '20251222']
file_numbers = ['20251227']

for file_number in file_numbers:   
    PlotData.plot_apple_and_model_data(file_number)