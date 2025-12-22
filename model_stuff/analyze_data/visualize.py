import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Load your full dataset
df = pd.read_csv("model_stuff/data/test/bigboy_with_hr_mean.csv") 

palette = sns.color_palette("viridis", n_colors=df['psg_label'].nunique())

# --- PLOT 1: Feature Distributions (Box Plots) ---
features = ['hr_mean', 'hr_std', 'count_feature', 'cosine_feature']
plt.figure(figsize=(16, 10))
for i, col in enumerate(features):
    plt.subplot(2, 2, i+1)
    sns.boxplot(data=df, x='psg_label', y=col, palette=palette)
    plt.title(f'Distribution of {col} by Sleep Stage')
plt.tight_layout()
plt.show()

# --- PLOT 2: Feature Overlap (KDE/Density Plots) ---
plt.figure(figsize=(12, 6))
sns.kdeplot(data=df, x='hr_mean', hue='psg_label', fill=True, common_norm=False, palette=palette)
plt.title('Heart Rate Density: Where do stages overlap?')
plt.xlabel('Heart Rate (Normalized/Mean)')
plt.show()

# --- PLOT 3: Transition Matrix ---
transitions = pd.crosstab(df['psg_label'].shift(1), df['psg_label'], normalize='index')

plt.figure(figsize=(10, 8))
sns.heatmap(transitions, annot=True, fmt='.2f', cmap='YlGnBu')
plt.title('Transition Probabilities (Row: Previous Stage -> Column: Next Stage)')
plt.xlabel('Next Stage')
plt.ylabel('Current Stage')
plt.show()

print("Transition Matrix:")
print(transitions)