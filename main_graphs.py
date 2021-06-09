import graphs
import numpy as np
import pandas as pd
#%%
"""
Setting the variables for the experiment (to be used in GUI)
All numbers should be able to change
"""
#Aquire N counts measurments
N = 10

#TCP IP Address of your system (default 192.168.1.1)
tcp_ip_address = "192.168.1.163"

#The control port (default 12000)
control_port = 12000

#and the port emitting the photon Counts (default 12345)
counts_port = 12345  
 
# laser IP Adress
laserip = '192.168.1.149'

# laser channel number
laserchannel='5'    

number_of_detectors = 8
#%%
"""
Variables for plotting
"""

# since it breaks down, break down the measurements in blocks
cali_waves1=np.linspace(1260,1360,11)
cali_waves2=np.linspace(1370,1480,12)
cali_waves3 = np.linspace(1490,1600,12)
cali_waves4 = np.linspace(1610,1650,5)

# sets bias current at start of experiment
std_bias = funcs.current_setter(number_of_detectors, 25)

# range of currents
xIb = np.linspace(0,40,15)

# get N counts for all detectors using a varying bias current
list_Ib = funcs.current_setter(number_of_detectors, xIb)

# range of wavelengths for plot
waves = np.arange(1260, 1660, 10)

#%%
"""
plot laser stability
"""
waves = np.arange(1260, 1660, 10)

file = pd.read_excel("PowerLasergood.xlsx")
file = file.iloc[:, 1:]

graphs.laser_stability_plot(file, waves)

#%%
"""
read in the calibration data
"""
dflaserP1 = pd.read_excel("P1.xlsx")
dflaserP1 = dflaserP1.iloc[: , 1:]
dflaserP2 = pd.read_excel("P2.xlsx")
dflaserP2 = dflaserP2.iloc[: , 1:]


dflaserP1=dflaserP1.drop(dflaserP1.index[1])

#%%

"""
Get ratios between measurement arm and reference arm
"""
ratios, dbratios = graphs.getratios2(dflaserP1, dflaserP2)

#%%
""" 
plot calibration measurements
"""

waves = np.arange(1260, 1610, 10)
P1 = pd.read_excel("P1.xlsx").iloc[:,1:]
P2 = pd.read_excel("P2.xlsx").iloc[:,1:]

graphs.laser_stability_plot(P1, waves)
graphs.laser_stability_plot(P2, waves)
   
#%%
"""
read in measurement data, with sleep timer
"""
detect1260 = []
for i in range(4,7):
    detections = pd.read_excel("meas1260V"+str(i)+".xlsx")
    detections = detections.iloc[6].tolist()[1:] #skip first value, only detector 7 was in use
    detect1260.append(detections)
    
detect1370 = []
for i in range(4,7):
    detections = pd.read_excel("meas1370V"+str(i)+".xlsx")
    detections = detections.iloc[6].tolist()[1:7] #skip first value, only detector 7 was in use, after 1420 values are useless
    detect1370.append(detections)

    
pwr1260 = []
for i in range(4,7):   
    pwrs = pd.read_excel("pwr1260V"+str(i)+".xlsx")
    pwr1260.append(pwrs)
    
pwr1370 = []
for i in range(4,7):    
    pwrs = pd.read_excel("pwr1370V"+str(i)+".xlsx").iloc[:,0:7]
    pwr1370.append(pwrs)


#%%
"""
Calculate efficiency of the system, 1260-1360, sleep timer
"""
for j in range(len(detect1260)):
    total_photons, efficiency = graphs.photon_eff(cali_waves1, ratios, pwr1260[j], number_of_detectors, detect1260[j], j+3)
    graphs.ploteffwav(cali_waves1, efficiency, j)

#%%
"""
Calculate efficiency of the system, 1370-1480
"""
for j in range(len(detect1370)):
    total_photons, efficiency = graphs.photon_eff(cali_waves2[0:6], ratios, pwr1370[j], number_of_detectors, detect1370[j], j+3)
    graphs.ploteffwav(cali_waves2, efficiency, j)