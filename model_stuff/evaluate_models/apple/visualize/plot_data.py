import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

class PlotData():
    def plot_apple_and_model_data(file_number):
        apple_file_path = f'sleep_data_logs/sleep_data_{file_number}.json' 
        model_results_path = f'model_stuff/model_results/{file_number}_model_results.txt'
        metadata_path = f'sleep_data_logs/start_time_{file_number}.json'

        # FIX: Use pandas to create a timezone-aware UTC timestamp
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
            model_start_dt = pd.to_datetime(meta['startTime'], unit='s', utc=True)

        with open(apple_file_path, 'r') as f:
            apple_data = json.load(f)

        with open(model_results_path, 'r') as f:
            model_raw_values = [int(line.strip()) for line in f if line.strip().isdigit()]

        df_apple = pd.DataFrame(apple_data)
        # Ensure Apple data is also treated as UTC (it usually is by default if 'Z' is present)
        df_apple['startDate'] = pd.to_datetime(df_apple['startDate'], utc=True)
        df_apple['endDate'] = pd.to_datetime(df_apple['endDate'], utc=True)

        overall_start_time = min(df_apple['startDate'].min(), model_start_dt)

        apple_stage_map = {
            "Awake": 3, "REM Sleep": 2, "Light/Core Sleep": 1, "Deep Sleep": 0, "In Bed": 3
        }
        df_apple['plot_val'] = df_apple['stage'].map(apple_stage_map)
        
        df_apple['start_hours'] = (df_apple['startDate'] - overall_start_time).dt.total_seconds() / 3600.0
        df_apple['end_hours'] = (df_apple['endDate'] - overall_start_time).dt.total_seconds() / 3600.0

        def map_model_to_apple(val):
            if val == 0: return 3
            if val == 1: return 1
            if val == 2: return 1
            if val == 3: return 0
            if val == 5: return 2
            return None
        
        model_plot_vals = [map_model_to_apple(v) for v in model_raw_values]

        model_offset_seconds = (model_start_dt - overall_start_time).total_seconds()
        model_hours = [((i * 30) + model_offset_seconds) / 3600.0 for i in range(len(model_plot_vals))]

        plt.figure(figsize=(14, 6))

        plt.step(df_apple['start_hours'], df_apple['plot_val'], where='post', 
                label='Apple Watch', color='#007AFF', linewidth=2.5)
        
        last_apple = df_apple.iloc[-1]
        plt.hlines(y=last_apple['plot_val'], xmin=last_apple['start_hours'], xmax=last_apple['end_hours'], 
                colors='#007AFF', linewidth=2.5)

        plt.step(model_hours, model_plot_vals, where='post', 
                label='Model Prediction', color='#FF9500', linewidth=1.5, linestyle='--')

        plt.yticks([0, 1, 2, 3], ["Deep", "Core", "REM", "Awake"])
        # Format the datetime in the label (converting to local time if you prefer readability, or keep as UTC)
        plt.xlabel(f"Hours Since {overall_start_time.strftime('%I:%M %p')}")
        plt.title(f"Sleep Comparison (Aligned) | Date: {file_number}")
        plt.legend(loc='upper right')
        plt.ylim(-0.5, 3.5)
        plt.grid(axis='y', linestyle='--', alpha=0.3)
        plt.axhspan(1.5, 2.5, color='purple', alpha=0.05)
        plt.axhspan(-0.5, 0.5, color='blue', alpha=0.05)
        
        plt.tight_layout()
        plt.show()