#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt
from scipy.signal import savgol_filter
from scipy.optimize import minimize_scalar
from scipy.interpolate import CubicSpline

# %%


# todo set this as a default stating folder for the gui selection
ordner = Path(r"/mnt/c/DLR/Data")


hot_dateien = sorted(ordner.glob("*hot.csv"))
cold_dateien = sorted(ordner.glob("*cold.csv"))

print("Number of averaged files:", len(hot_dateien))

m = 1

data = pd.read_csv(hot_dateien[0])

IF = data.loc[data.iloc[:,2] == 0, data.columns[1]].to_numpy(dtype = float)
IF = np.array([np.mean(IF[i:i+m]) for i in range(0, len(IF), m)])


spectrum_index = np.linspace(0, 19, 20)


def csv_mitteln(datei_h, datei_c):

    data_h = pd.read_csv(datei_h)
    data_c = pd.read_csv(datei_c)
    
    count_all_h = []
    count_all_c = []

    for n in spectrum_index:

        count_h = data_h.loc[data_h.iloc[:,2] == n, data_h.columns[3]].to_numpy(dtype = float)
        count_c = data_c.loc[data_c.iloc[:,2] == n, data_c.columns[3]].to_numpy(dtype = float)
        
        y = (count_h / count_c)**2
        
        Y = np.mean(y)
        
        #if Y >= 1.015:
        
        count_all_h.append(count_h)
        count_all_c.append(count_c)

    count_h = np.mean(count_all_h, axis =0)
    count_h = count_h**2
    
    count_c = np.mean(count_all_c, axis =0)
    count_c = count_c**2
    

    return count_h, count_c



count_hot_all = []
count_cold_all = []

for datei_h, datei_c in zip(hot_dateien, cold_dateien):
    count_h, count_c = csv_mitteln(datei_h, datei_c)
    count_hot_all.append(count_h)
    count_cold_all.append(count_c)
    


count_hot = np.mean(count_hot_all, axis =0)
count_hot = np.array([np.mean(count_hot[i:i+m]) for i in range(0, len(count_hot), m)])

plt.plot(IF, count_hot, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load")
plt.show()


count_cold = np.mean(count_cold_all, axis =0)
count_cold = np.array([np.mean(count_cold[i:i+m]) for i in range(0, len(count_cold), m)])

plt.plot(IF, count_cold, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load")
plt.show()


# %%

mask_cut = (IF >= 0.17) & (IF <= 0.7)

count_hot_cut = count_hot[mask_cut]
IF_cut = IF[mask_cut]

plt.plot(IF_cut, count_hot_cut, marker = "o", markersize = 1)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load")
plt.show()


count_cold_cut = count_cold[mask_cut]

IF_cut = IF[mask_cut]


plt.plot(IF_cut, count_cold_cut, marker = "o", markersize = 1)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load")
plt.show()


# %%


median = medfilt(count_hot_cut, kernel_size = 11)
spike_mask = np.abs(count_hot_cut - median) > 8e5



count_hot_clean = count_hot_cut[~spike_mask]

IF_clean = IF_cut[~spike_mask]

count_cold_clean = count_cold_cut[~spike_mask]


plt.plot(IF_clean, count_hot_clean, color = "r" , marker = "o", markersize = 1, linewidth = 0, label = "hot")
plt.plot(IF_clean, count_cold_clean,color = "b" , marker = "o", markersize = 1, linewidth = 0, label = "cold")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load - without spikes")
plt.legend()
plt.show()

# %%

y = count_hot_clean / count_cold_clean 

plt.plot(IF_clean, y, marker = "o", markersize = 1)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("y-factor")
plt.title("Y-factor")
plt.show()


mask_peak = np.ones(len(IF_clean), dtype = bool)

# for i, freq in enumerate(IF_clean):
#     if (freq <= 0.326):
#         if (freq >= 0.25):
            
#             mask_peak[i] = False


for i, freq in enumerate(IF_clean):
    if (freq <= 0.36):
        if (freq >= 0.2):
            
            mask_peak[i] = False


plt.plot(IF_clean[~mask_peak], y[~mask_peak], marker = "o", markersize = 1, linewidth = 0)
plt.plot(IF_clean[mask_peak], y[mask_peak], marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("y-factor")
plt.title("Y-factor")
plt.show()


# %%

degree = 6

coeffs = np.polyfit(IF_clean[mask_peak], y[mask_peak], degree)

baseline_poly = np.polyval(coeffs, IF_clean)

plt.figure()

plt.plot(IF_clean, y, marker = "o", markersize = 1, linewidth = 0)
plt.plot(IF_clean[mask_peak], y[mask_peak], marker = "o", markersize = 1, linewidth = 0)
plt.plot(IF_clean, baseline_poly, color = "r", label = "polynomfit")
plt.legend()
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("y-factor")
plt.show()


# %%

cold_base = count_hot_clean / baseline_poly

plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, linewidth = 0, label = "data")
plt.plot(IF_clean, cold_base, color = "r", label = "hot load / y")
plt.legend()
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()

# %%


cold_peak = count_cold_clean - cold_base

plt.plot(IF_clean, cold_peak, color = "r", label = "hot load / y")
plt.legend()
plt.xlabel("IF - frequency [GHz]")
plt.vlines(0.2825, -100000, 600000)
plt.vlines(0.3025, -100000, 600000)
plt.ylabel("count^2")
plt.show()



# %%

freq_sim = []
bright_T = []

with open("/Users/antonia/Downloads/Sim32km,4deg.txt", "r", encoding = "utf-8") as data:
    
    next(data, None)
    
    for zeile in data:
        
        split = zeile.strip().split()
        
        if len(split) >= 2:
            freq_sim.append(float(split[0]))
            bright_T.append(float(split[1]))

freq_sim = np.array(freq_sim[:], dtype = float)
bright_T = np.array(bright_T[:], dtype = float)

freq_sim = abs(freq_sim/10**9 - 236.0)
freq_sim = freq_sim[::-1]
bright_T = bright_T[::-1]

freq_sim = freq_sim[8000:]
bright_T = bright_T[8000:]

print(freq_sim)

plt.plot(freq_sim, bright_T , color = "r", marker = "o", markersize = 1, linewidth = 0)
plt.legend()
plt.show()


# %%

mask_sim = (IF_clean >= min(freq_sim)) & (IF_clean <= max(freq_sim))

IF_sim = IF_clean[mask_sim]


# %%


bright_sim = np.interp(IF_sim, freq_sim, bright_T)

#plt.plot(IF_clean[mask_sim], count_cold_clean[mask_sim], marker = "o", markersize = 1, linewidth = 0, label = "data")
plt.plot(IF_sim, bright_sim, color = "r" , marker = "o", markersize = 1, linewidth = 0, label = "simulation")
plt.ylabel("Brightness Temperature [K]")
plt.xlabel("IF - frequency [GHz]")
plt.legend()
plt.show()


# %%

bright_T_data = (count_cold_clean - cold_base) / (count_hot_clean - cold_base) * 300 * 2 

bright_T_data = bright_T_data * 2.8

plt.plot(IF_clean[mask_sim], bright_T_data[mask_sim], marker = "o", markersize = 1, linewidth = 0, label = "data")
plt.plot(IF_sim, bright_sim, color = "r" , marker = "o", markersize = 1, linewidth = 0, label = "simulation")
plt.ylabel("Brightness Temperature [K]")
plt.xlabel("IF - frequency [GHz]")
plt.ylim(-200, 300)
plt.legend()
plt.show()






















