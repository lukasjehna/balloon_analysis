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

# Savitzky-Golay filter without averaging

ordner = Path(r"/Users/antonia/Desktop/Kiruna_01Uhr")


hot_dateien = sorted(ordner.glob("*hot.csv"))
cold_dateien = sorted(ordner.glob("*cold.csv"))

print("Number of averaged files:", len(hot_dateien))


data = pd.read_csv(hot_dateien[0])

IF = data.loc[data.iloc[:,2] == 0, data.columns[1]].to_numpy(dtype = float)


spectrum_index = np.linspace(0, 19, 20)


def csv_mitteln(datei_h, datei_c):

    data_h = pd.read_csv(datei_h)
    data_c = pd.read_csv(datei_c)
    
    count_all_h = []
    count_all_c = []

    for n in spectrum_index:

        count_h = data_h.loc[data_h.iloc[:,2] == n, data_h.columns[3]].to_numpy(dtype = float)
        count_c = data_c.loc[data_c.iloc[:,2] == n, data_c.columns[3]].to_numpy(dtype = float)
        
        
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

plt.plot(IF, count_hot, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load")
plt.show()


count_cold = np.mean(count_cold_all, axis =0)

plt.plot(IF, count_cold, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load")
plt.show()


# %%

mask_cut = (IF >= 0.1) & (IF <= 0.9)

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
spike_mask = np.abs(count_hot_cut - median) > 2e5


count_hot_clean = count_hot_cut[~spike_mask]

IF_clean = IF_cut[~spike_mask]


plt.plot(IF_clean, count_hot_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load - without spikes")
plt.show()



count_cold_clean = count_cold_cut[~spike_mask]


plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load - without spikes")
plt.show()



# %%

anomaly_hot = np.zeros_like(count_hot_clean)


anomaly_hot = savgol_filter(count_hot_clean, window_length = 15, polyorder = 2)

plt.plot(IF_clean, count_hot_clean, color = "b", linewidth = 0,  marker = "o", markersize = 1)

plt.plot(IF_clean, anomaly_hot, color = "r")
plt.title("Fitted Hot Load")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()


# %%


def error(offset):
    
    indiv_error = count_cold_clean - (anomaly_hot * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)


baseline_anom_off = anomaly_hot * offset

plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, label = "cold", linewidth = 0)
plt.plot(IF_clean, baseline_anom_off, color = "r", label = "baseline")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load and baseline fit * factor")
plt.legend()
plt.show()



count_cold_cor = count_cold_clean - baseline_anom_off

plt.plot(IF_clean, count_cold_cor, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Corrected Cold Load (cold - hot, baseline * factor)")
plt.show()


# %%

# Without avering and without fit / filter / spline

def error(offset):
    
    indiv_error = count_cold_clean - (count_hot_clean * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)

count_hot_clean2 = count_hot_clean * offset

count_cold_cor2 = count_cold_clean - count_hot_clean2

plt.plot(IF_clean, count_cold_cor2, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Corrected Cold Load (cold - hot * factor, without fit)")
plt.show()




# %%








# %%

# With average und Savitzky-Golay Filter:
    
ordner = Path(r"/Users/antonia/Desktop/Kiruna_01Uhr")


hot_dateien = sorted(ordner.glob("*hot.csv"))
cold_dateien = sorted(ordner.glob("*cold.csv"))

print("Anzahl gemittleter Datein:", len(hot_dateien))

m = 3    # Anzahl der werte über die gemittlet wird

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


mask_cut = (IF >= 0.1) & (IF <= 0.4)

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
spike_mask = np.abs(count_hot_cut - median) > 1e6


count_hot_clean = count_hot_cut[~spike_mask]

IF_clean = IF_cut[~spike_mask]


plt.plot(IF_clean, count_hot_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load - without spikes")
plt.show()



count_cold_clean = count_cold_cut[~spike_mask]


plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load - without spikes")
plt.show()


# %%

anomaly_hot = np.zeros_like(count_hot_clean)


anomaly_hot = savgol_filter(count_hot_clean, window_length = 15, polyorder = 2)

plt.plot(IF_clean, count_hot_clean, color = "b", linewidth = 0,  marker = "o", markersize = 1)

plt.plot(IF_clean, anomaly_hot, color = "r")
plt.title("Fitted Hot Load")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()


# %%


def error(offset):
    
    indiv_error = count_cold_clean - (anomaly_hot * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)


baseline_anom_off = anomaly_hot * offset

plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, label = "cold", linewidth = 0)
plt.plot(IF_clean, baseline_anom_off, color = "r", label = "baseline")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Cold Load and baseline fit * factor")
plt.legend()
plt.show()



count_cold_cor = count_cold_clean - baseline_anom_off

plt.plot(IF_clean, count_cold_cor, marker = "o", markersize = 1,  linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Corrected Cold Load (cold - hot, baseline * factor)")
plt.show()

# %%


def error(offset):
    
    indiv_error = count_cold_clean - (count_hot_clean * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)

count_hot_clean2 = count_hot_clean * offset

count_cold_cor2 = count_cold_clean - count_hot_clean2


plt.plot(IF_clean, count_cold_cor2, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Corrected Cold Load (cold - hot * factor, without fit)")
plt.show()

plt.plot(IF_clean, count_hot_clean2, color = "r", marker = "o", markersize = 1, linewidth = 0, label = "hot")
plt.plot(IF_clean, count_cold_clean, color = "b",  marker = "o", markersize = 1, linewidth = 0, label = "cold")
plt.legend()
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()

# %%









# %%

# mit mitteln und spline:
    
ordner = Path(r"/Users/antonia/Desktop/Kiruna_01Uhr")


hot_dateien = sorted(ordner.glob("*hot.csv"))
cold_dateien = sorted(ordner.glob("*cold.csv"))

print("Anzahl gemittleter Datein:", len(hot_dateien))

m = 3

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


mask_cut = (IF >= 0.2) & (IF <= 0.4)

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
spike_mask = np.abs(count_hot_cut - median) > 1e6


count_hot_clean = count_hot_cut[~spike_mask]

IF_clean = IF_cut[~spike_mask]


plt.plot(IF_clean, count_hot_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Hot Load - without spikes")
plt.show()



count_cold_clean = count_cold_cut[~spike_mask]


plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Cold Load - without spikes")
plt.show()


# %%

IF_spline = IF_clean[::3]
count_spline = count_hot_clean[::3]

spline_func = CubicSpline(IF_spline, count_spline)

spline = spline_func(IF_clean)

plt.plot(IF_clean, count_hot_clean, color = "b")
plt.plot(IF_clean, spline, color = "r")
#plt.plot(IF_clean[::10], count_hot_clean[::10], color = "c", linewidth = 0, marker = "o", markersize = 2)
plt.title("Spline - Hot Load")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()


# %%


def error(offset):
    
    indiv_error = count_cold_clean - (spline * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)


baseline_anom_off = spline * offset

plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, label = "cold", linewidth = 0)
plt.plot(IF_clean, baseline_anom_off, color = "r", label = "baseline")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Cold Load and spline * factor")
plt.legend()
plt.show()



count_cold_cor = count_cold_clean - baseline_anom_off

plt.plot(IF_clean, count_cold_cor, marker = "o", markersize = 1,  linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Corrected Cold Load (cold - hot, spline * factor)")
plt.show()

# %%



def error(offset):
    
    indiv_error = count_cold_clean - (count_hot_clean * offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)

count_hot_clean2 = count_hot_clean * offset

count_cold_cor2 = count_cold_clean - count_hot_clean2


plt.plot(IF_clean, count_cold_cor2, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Corrected Cold Load (cold - hot * factor, without fit)")
plt.show()



# %%





# %%

# mit spline und ohne mitteln:
    
ordner = Path(r"/Users/antonia/Desktop/Kiruna_01Uhr")


hot_dateien = sorted(ordner.glob("*hot.csv"))
cold_dateien = sorted(ordner.glob("*cold.csv"))

print("Anzahl gemittleter Datein:", len(hot_dateien))


data = pd.read_csv(hot_dateien[0])

IF = data.loc[data.iloc[:,2] == 0, data.columns[1]].to_numpy(dtype = float)



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
        
        #if Y >= 1.15:
        
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

plt.plot(IF, count_hot, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Hot Load")
plt.show()


count_cold = np.mean(count_cold_all, axis =0)

plt.plot(IF, count_cold, marker = "o", markersize = 2)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.title("Mean Cold Load")
plt.show()

# %%


mask_cut = (IF >= 0.1) & (IF <= 0.5)

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
spike_mask = np.abs(count_hot_cut - median) > 1e6


count_hot_clean = count_hot_cut[~spike_mask]

IF_clean = IF_cut[~spike_mask]


plt.plot(IF_clean, count_hot_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Hot Load - without spikes")
plt.show()



count_cold_clean = count_cold_cut[~spike_mask]


plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Cold Load - without spikes")
plt.show()


# %%

IF_spline = IF_clean[::10]
count_spline = count_hot_clean[::10]

spline_func = CubicSpline(IF_spline, count_spline)

spline = spline_func(IF_clean)

plt.plot(IF_clean, count_hot_clean, color = "b")
plt.plot(IF_clean, spline, color = "r")
#plt.plot(IF_clean[::10], count_hot_clean[::10], color = "c", linewidth = 0, marker = "o", markersize = 2)
plt.title("Spline - Hot Load")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count^2")
plt.show()


# %%


def error(offset):
    
    indiv_error = count_cold_clean - (spline + offset)
    
    return np.sum(indiv_error**2)

result = minimize_scalar(error, bounds = (-1e8, 1e8), method = "bounded")

offset = result.x

print(offset)


baseline_anom_off = spline + offset

plt.plot(IF_clean, count_cold_clean, marker = "o", markersize = 1, label = "cold", linewidth = 0)
plt.plot(IF_clean, baseline_anom_off, color = "r", label = "baseline")
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Mean Cold Load and spline * factor")
plt.legend()
plt.show()



count_cold_cor = count_cold_clean - baseline_anom_off

plt.plot(IF_clean, count_cold_cor, marker = "o", markersize = 1,  linewidth = 0)
plt.xlabel("IF - frequency [GHz]")
plt.ylabel("count (mean)")
plt.title("Corrected Cold Load (cold - hot, spline + offset)")
plt.show()














