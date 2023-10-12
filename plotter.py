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

fig1, axs1 = plt.subplots(nrows=3, figsize=(30, 15))
axs1[0].set_title(f'Steering Angular Position vs. Time')
axs1[0].set_xlabel('Time (s)')
axs1[0].set_ylabel('Angular Position (rad)')
axs1[1].set_title(f'Steering Angular Velocity vs. Time')
axs1[1].set_xlabel('Time (s)')
axs1[1].set_ylabel('Angular Velocity (rad/s)')
axs1[2].set_title(f'Steering Angular Acceleration vs. Time')
axs1[2].set_xlabel('Time (s)')
axs1[2].set_ylabel('Angular Acceleration (rad/s^2)')

fig2, axs2 = plt.subplots(nrows=2, figsize=(20, 10))
axs2[0].set_title(f'Angular Velocity Distribution')
axs2[0].set_xlabel('Angular Velocity (rad/s)')
axs2[1].set_title(f'Angular Acceleration Distribution')
axs2[1].set_xlabel('Angular Acceleration (rad/s^2)')

vels = []
accels = []
labels = []

for csv in sorted(os.listdir(CSV_DIR)):
  df = pd.read_csv(os.path.join(CSV_DIR, csv))
  position = df[CHANNEL].to_numpy()
  time = df['TimeLow [us/10]'].to_numpy()
  dt = np.diff(time)
  resets = np.argwhere(dt < 0).squeeze(axis=1) + 1
  positions = np.split(position, resets)
  times = np.split(time, resets)
  for i in range(len(positions)):
    time = (times[i] - times[i][0]) / 1e7
    name = csv.replace('.csv', '')

    # angular pos
    pos = positions[i]
    axs1[0].plot(time, pos, alpha=0.5, label=name)

    # angular vel
    time, vel = differentiate(time, pos)
    axs1[1].plot(time, vel, alpha=0.5, label=name)

    # angular accel
    time, accel = differentiate(time, vel)
    axs1[2].plot(time, accel, alpha=0.5, label=name)

    vels.append(vel)
    accels.append(accel)
    labels.append(name)

axs2[0].hist([np.abs(vel) for vel in vels], bins=50, stacked=True, edgecolor='none', label=labels)
axs2[1].hist([np.abs(accel) for accel in accels], bins=50, stacked=True, edgecolor='none', label=labels)

vel_99 = np.percentile(np.concatenate(vels), PERCENTILE)
accel_99 = np.percentile(np.concatenate(accels), PERCENTILE)
axs2[0].axvline(x=vel_99, linestyle='--', label=f'99th Percentile: {round(vel_99, 4)} rad/s')
axs2[1].axvline(x=accel_99, linestyle='--', label=f'99th Percentile: {round(accel_99, 4)} rad/s^2')

axs1[0].legend(loc='upper right', fontsize='9')
axs1[1].legend(loc='upper right', fontsize='9')
axs1[2].legend(loc='upper right', fontsize='9')
axs2[0].legend(loc='upper right', fontsize='9')
axs2[1].legend(loc='upper right', fontsize='9')
axs2[0].set_xlim(left=0.0)
axs2[1].set_xlim(left=0.0)

fig1.tight_layout()
fig1.savefig('steering_pot.png')
fig2.tight_layout()
fig2.savefig('steering_dist.png')
