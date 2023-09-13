import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CSV_DIR = 'drive_csvs'
CHANNEL = 'TC_SteeringRight (rads)'
PERCENTILE = 99

sns.set()

def differentiate(x, y):
  return x[:-1], np.diff(y) / np.diff(x)

fig, axs = plt.subplots(nrows=2, figsize=(8, 8))
axs[0].set_title(f'Angular Velocity Distribution')
axs[0].set_xlabel('Angular Velocity (rad/s)')
axs[0].set_xlim(right=0.9)
axs[1].set_title(f'Angular Acceleration Distribution')
axs[1].set_xlabel('Angular Acceleration (rad/s^2)')
axs[1].set_xlim(right=50.0)

vels = []
accels = []

for csv in os.listdir(CSV_DIR):
  df = pd.read_csv(os.path.join(CSV_DIR, csv))
  time = ((df['TimeLow [us/10]'] - df['TimeLow [us/10]'][0]) / 1e7).to_numpy()
  name = csv.replace('.csv', '')

  pos = df[CHANNEL].to_numpy()
  time, vel = differentiate(time, pos)
  time, accel = differentiate(time, vel)

  # angular vel dist
  axs[0].hist(np.abs(vel), bins=100, alpha=0.5, label=name)

  # angular accel dist
  axs[1].hist(np.abs(accel), bins=100, alpha=0.5, label=name)

  vels.append(vel)
  accels.append(accel)

vel_percentile = np.percentile(np.concatenate(vels), PERCENTILE)
accel_percentile = np.percentile(np.concatenate(accels), PERCENTILE)
axs[0].axvline(x=vel_percentile, linestyle='--', alpha=0.8, label=f'99th Percentile: {round(vel_percentile, 4)}')
axs[1].axvline(x=accel_percentile, linestyle='--', alpha=0.8, label=f'99th Percentile: {round(accel_percentile, 4)}')

axs[0].legend(fontsize='8')
axs[1].legend(fontsize='8')
plt.tight_layout()
fig.savefig('steering_dist.png')
