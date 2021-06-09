import functions as funcs
import graphs 
import numpy as np
import time
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

#%%
"""
Making the connection check with the system (should include all devices!):
    - SNSPD Driver
    - Attenuator
    - Tunable laser
    - Power meter
"""
ms_time, bias_current, trigger, number_of_detectors = funcs.start_snspd(N, tcp_ip_address, control_port, counts_port) # retrieves import exp parameters

#%%
"""
Setting more variables as the user wishes. Giving option to:
    - plot efficiency for a range of currents
    - plot count rate for a range of currents
    - plot efficiency for each wavelength at a set current
    - calibration measurements of the laser / system
    - monitor the power during measurements using the SNSPD
"""
# sets bias current at start of experiment
std_bias = funcs.current_setter(number_of_detectors, 25)

# range of currents
xIb = np.linspace(0,40,15)

# get N counts for all detectors using a varying bias current
list_Ib = funcs.current_setter(number_of_detectors, xIb)

# range of wavelengths for plot
waves = np.linspace(1260,1360,10)

# range of wavelengths for calibration measurements
# since the code overloads after long times, break down the measurements in blocks
cali_waves1=np.linspace(1260,1360,11)
cali_waves2=np.linspace(1370,1480,12)
cali_waves3 = np.linspace(1490,1600,12)
cali_waves4 = np.linspace(1610,1650,5)

# range of time intervals for calibration measurements
number_of_calimeasurements = 20
time_interval = 0.5
cali_times = np.linspace(0, 20, 20)

# range of time intervals for measurements
meas_times = np.linspace(0,10,20)

#%%
"""
get N counts for all detectors using a set bias current
"""
# acquire N counts for all detectors using a set bias current
avgs_detect, df =funcs.detected_counts(tcp_ip_address, control_port, counts_port,N, number_of_detectors, std_bias,0)

#%%
"""
get count rate for a range of current values at a set wavelength (not specified, should be set manually)
"""
avgscounts = funcs.count_rate(tcp_ip_address, control_port, counts_port,list_Ib, N, number_of_detectors)

#%%
"""
calibration measurements of the laser 
"""
# get stability measurements of the power of the laser for a set of wavelengths for a specified duration
laserdf, laserlist = funcs.laser_stability(cali_waves, number_of_calimeasurements, time_interval) 

#%%
"""
Two power meters for a range of wavelengths
"""

dflaserP1, dflaserP2, laserlistP1, laserlistP2 = funcs.calibration(cali_waves1, number_of_calimeasurements, time_interval)
#%%

dflaserP1, dflaserP2, laserlistP1, laserlistP2 = funcs.calibration(cali_waves2, number_of_calimeasurements, time_interval)
#%%

dflaserP1, dflaserP2, laserlistP1, laserlistP2 = funcs.calibration(cali_waves3, number_of_calimeasurements, time_interval)
#%%
#outside the range
dflaserP1, dflaserP2, laserlistP1, laserlistP2 = funcs.calibration(cali_waves4, number_of_calimeasurements, time_interval)
#%%
"""
SNSPD counts for range of wavelengths, also measuring power
"""
snspdcounts, powerfluctuations = funcs.measurements(tcp_ip_address, control_port, counts_port, N, number_of_detectors, Ib, waves, db, laserip,laserchannel)