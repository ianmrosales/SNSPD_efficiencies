from WebSQControl import WebSQControl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def current_setter(number_of_detectors, Irange):
    """
    This function sets the current for all detectors in the SNSPD system in one time
    INPUT:
        number_of_detectors: (INT)
        Irange: INT or LIST, specify the value(s) to be used as current (microA)
    """
    
    if isinstance(Irange, list):
        y = [[val]*number_of_detectors for val in Irange]
    elif isinstance(Irange, np.ndarray):
        y = [[val]*number_of_detectors for val in Irange]
    else:
        y = [Irange]*number_of_detectors
    return y

def start_snspd(N, tcp_ip_address, control_port, counts_port):
    """
    
    Starting the SNSPD driver and doing a system check. Returns present parameters of the system
    
    INPUT:
        tcp_ip_address (STR)
        control_port (INT)
        counts_port (INT)
        
    OUTPUT:
        ms_time = integration time of the system (INT)
        bias_current (LIST,INT)
        trigger (INT)
        number_of_detectors (INT) 
        
    """
    websq = WebSQControl(TCP_IP_ADR = tcp_ip_address, CONTROL_PORT = control_port, COUNTS_PORT = counts_port)
    websq.connect()
    
    #Acquire number of detectors in the system
    number_of_detectors =  websq.get_number_of_detectors()
    print("Your system has " + str(number_of_detectors) + ' detectors\n')
    
    print("Set integration time to 100 ms\n")
    websq.set_measurement_periode(100)   #time in ms
    
    print("Enable detectors\n")
    websq.enable_detectors(True)
    
    
    # Print out the parameters of the experiment
    ms_time = websq.get_measurement_periode()
    bias_current = websq.get_bias_current()
    trigger = websq.get_trigger_level()
    
    #Close connection
    websq.close()

    print("Read back set values")
    print("====================\n")
    print("Measurement Periode (ms): \t" + str(ms_time))
    print("Bias Currents in uA: \t\t" +    str(bias_current))
    print("Trigger Levels in mV: \t\t" +   str(trigger))
    
    # N measurements
    print("Aquire " + str(N) + " counts measurements")
    print("============================\n")
    return ms_time, bias_current, trigger, number_of_detectors

def detected_counts(tcp_ip_address, control_port, counts_port, N, number_of_detectors, Ib,wav):
    """

    Parameters
    ----------
    tcp_ip_address (STR)
    control_port (INT)
    counts_port (INT)
    N = number of measurements to be taken (INT)
    number_of_detectors
    Ib = bias current (LIST), for every detector a value
    wav = INT, used for naming the xlsx file

    Returns
    -------
    A DataFrame containing all counts, An DataFrame containing the averages per detector.

    """
    websq = WebSQControl(TCP_IP_ADR = tcp_ip_address, CONTROL_PORT = control_port, COUNTS_PORT = counts_port)
    websq.connect()
    
    # start by setting bias current
    websq.set_bias_current(current_in_uA     = Ib)
    
    ms_time = websq.get_measurement_periode()
    
    #Aquire N counts measurements
    #Returns an array filled with N numpy arrays each
    #containing as first element a time stamp and then the detector counts in ascending order.
    counts = websq.aquire_cnts(N)
    for i in range(1,len(counts)):
        counts[i]=counts[i]*1/(ms_time*10**(-3))
        
    # create dataframe out of the measurements
    df = pd.DataFrame()
    for i in range(len(counts)):
        df = df.append(pd.DataFrame(counts[i]).T)
    
    # some styling to the indices to make it easier to extract data
    headers = ["Channel "+str(1+i) for i in range(number_of_detectors)]
    meas = [i for i in range(1,N+1)]
    headers.insert(0, "Timestamp")

    df.set_axis(headers, axis=1, inplace=True)
    df.set_axis(meas, axis = 0, inplace=True)
    
    # remove noise in the used detector
    # add more of such lines if more ports are used
    df = df[df["Channel 7"] > 20000] 
    
    # used if this function is used in a loop for different wavelengths
    df.to_excel("counts"+str(wav)+".xlsx") 
    
    # calculate average counts for each column (detector) in the dataframe
    avgs_detect = df.mean(axis=0)  
    websq.close()
    
    return avgs_detect, df

def count_rate(tcp_ip_address, control_port, counts_port, list_Ib, N, number_of_detectors):
    """
    This function measures the photon count rate for a range of current values values
    per detector in the system at a set wavelength (set manually)
    
    Parameters
    -------
    list_Ib: a nested list containing different bias currents
    List inside the list contains currents specified for each detector
    xIb: the range of values for Ib used for the plot

    Returns
    -------
    avgscounts: a list of avg photon counts.

    """

    # create an empty list to store the photon counts
    avgscounts=[]
    for i in list_Ib:
        avgs = detected_counts(tcp_ip_address, control_port, counts_port, N, number_of_detectors, i,0)[0].tolist()
        
    # since the output of the detected_counts() is a list (containing timestamp), 
    # the timestamp is removed and all other values are appended to a list  
        for j in avgs[1:]:
            avgscounts.append(j)
    return avgscounts
    
def get_power():
    import time
    """
    This function retrieves the power from the THOR PM100 power meter.
    Works only if one power meter is connected to the system
    
    OUTPUT:
        p = power (INT)
    """

    from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_double
    from TLPM import TLPM

    # establish connection
    tlPM = TLPM()
    deviceCount = c_uint32()
    tlPM.findRsrc(byref(deviceCount))
    
    print("devices found: " + str(deviceCount.value))
    
    resourceName = create_string_buffer(1024)
    
    for i in range(0, deviceCount.value):
        tlPM.getRsrcName(c_int(i), resourceName)
        print(c_char_p(resourceName.raw).value)
        break
    
    tlPM.close()
    
    # open the power meter and get power value    
    tlPM = TLPM()

        #set wavelength power meter
    tlPM.open(resourceName, c_bool(True), c_bool(True))
    
    time.sleep(1)
    power_fluct = np.zeros(10)
    
    j=0    
    while j<10:
           
        power =  c_double()
        tlPM.measPower(byref(power))
    
        print(power.value)
    
        p = power.value
        
        power_fluct[j]=p
        time.sleep(0.3)
        
        print(p)
        j = j+1
    tlPM.close() 
    pwr = np.average(power_fluct[2:])
    print("Power =", pwr )
    return pwr

  
def calibration(waves, number_of_calimeasurements, time_interval):   
    """
    Perform measurements on two powermeters for a range of wavelengths. Store the output in xlsx files
    INPUT:
        waves = range of wavelengths (LIST)
        number_of_calimeasurements = the number of power measurements to be taken at each wavelength
        time_interval = specify the amount of time to wait between each measurement
        
    OUTPUT:
        dflaserP1 = DataFrame containing all powers of powermeter 1, sorted per wavelength
        dflaserP2 = DataFrame containing all powers of powermeter 2, sorted per wavelength
        laserlistP1 = List containing all powers of powermeter 1, sorted per wavelength
        laserlistP2 = List containing all powers of powermeter 2, sorted per wavelength
    
    """
    global resourceNameP1, resourceNameP2
    import laser
    import time
    import Attenuator
    from TLPM import TLPM
    from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
    
    # connect with the equipment
    l = laser.Laser()
    l.open_port('192.168.1.149','5') # connects
    d = Attenuator.Attenuator()
    d.open_port('192.168.1.148','18')
    d.setAtt(0)    
    tlPM = TLPM()
    deviceCount = c_uint32()
    tlPM.findRsrc(byref(deviceCount))
    
    print("devices found: " + str(deviceCount.value))
    
    resourceNameP1 = create_string_buffer(1024)
    resourceNameP2 = create_string_buffer(1024)
     
    tlPM.getRsrcName(c_int(0), resourceNameP1)
    tlPM.getRsrcName(c_int(1), resourceNameP2)
    
    tlPM.close()

    # fill up the df
    laserlistP1 = []
    laserlistP2 = []
    
    for wave in waves:
        print(wave)
        l.setWVL(wave)

        d.setWVL(wave)
        print("================================")
        print("The wavelength is now set to:",l.getWVL())
        
        power_fluctP1 = []
        power_fluctP2 = []
        
        j = 0
        
        tlPM = TLPM()

        tlPM.open(resourceNameP1, c_bool(True), c_bool(True))
        
        waveset =  c_double(wave)
        tlPM.setWavelength(waveset)
        print("P1 values:")
        
        while j < number_of_calimeasurements:
            
            power =  c_double()
            tlPM.measPower(byref(power))

            print(power.value)
        
            p = power.value
            
            power_fluctP1.append(p)

            j = j+1
            time.sleep(time_interval)   
        
        tlPM.close()        
        laserlistP1.append(power_fluctP1)
                
        i = 0
        tlPM = TLPM()
        tlPM.open(resourceNameP2, c_bool(True), c_bool(True))
        
        waveset =  c_double(wave)
        tlPM.setWavelength(waveset)
        print("P2 values:")
        
        while i < number_of_calimeasurements:
            
            power =  c_double()
            tlPM.measPower(byref(power))

            print(power.value)
        
            p = power.value
            
            power_fluctP2.append(p)

            i = i+1
            time.sleep(time_interval)   
        

        tlPM.close()  

        laserlistP2.append(power_fluctP2)
        
    dflaserP1 = pd.DataFrame(laserlistP1).T
    headers = [i for i in waves]
    meas = [i for i in range(1,number_of_calimeasurements+1)]
    
    dflaserP1.set_axis(headers, axis=1, inplace=True)
    dflaserP1.set_axis(meas, axis = 0, inplace=True)
    dflaserP1.to_excel('powerfluctP1.xlsx')
    
    
    dflaserP2 = pd.DataFrame(laserlistP2).T
    dflaserP2.set_axis(headers, axis=1, inplace=True)
    dflaserP2.set_axis(meas, axis = 0, inplace=True)
    dflaserP2.to_excel('powerfluctP2.xlsx')
    
    return dflaserP1, dflaserP2, laserlistP1, laserlistP2

def laser_stability(waves, number_of_calimeasurements, time_interval):
    """
    This function measures the stability of the laser across a range of wavelengths
    taking power measurements every specified time interval

    Parameters
    ----------
    waves : LIST
        LIST CONTAINING LIST OF WAVELENGTH VALUES.
    times : LIST
        DESCRIPTION.

    Returns
    -------
    df : DATAFRAME
        DF CONTAINING THE POWER FLUCTUATIONS OF THE LASER, EACH COLUMN BEING ANOTHER WAVELENGTH

    """
    global resourceName
    import laser
    import time
    from TLPM import TLPM
    from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
    # connect with the equipment
    l = laser.Laser()
    l.open_port('192.168.1.149','5') # connects
    tlPM = TLPM()
    
    resourceName = create_string_buffer(1024)
    deviceCount = c_uint32()
    tlPM.findRsrc(byref(deviceCount))
    
    for i in range(0, deviceCount.value):
        tlPM.getRsrcName(c_int(i), resourceName)
        
    tlPM.close()    

    # fill up the df
    laserlist = []# pd.DataFrame(columns = waves)
    for wave in waves:
        print(wave)
        l.setWVL(wave)
        print("================================")
        print("The wavelength is now set to:",l.getWVL())
        
        power_fluct = []
        
        j = 0
        tlPM = TLPM()  
        tlPM.open(resourceName, c_bool(True), c_bool(True))
        
        waveset =  c_double(wave)
        tlPM.setWavelength(waveset)
        
        while j < number_of_calimeasurements:
            
            power =  c_double()
            tlPM.measPower(byref(power))

            print(power.value)
        
            p = power.value
            
            power_fluct.append(p)

            j = j+1
            time.sleep(time_interval)
            
        tlPM.close()
        laserlist.append(power_fluct)
        
    dflaser = pd.DataFrame(laserlist).T
    headers = [i for i in waves]
    meas = [i for i in range(1,number_of_calimeasurements+1)]
    dflaser.set_axis(headers, axis=1, inplace=True)
    dflaser.set_axis(meas, axis = 0, inplace=True)
    dflaser.to_excel('powerfluct.xlsx')
    
    return dflaser, laserlist

def measurements(tcp_ip_address, control_port, counts_port, N, number_of_detectors, Ib, waves, db, laserip,laserchannel):
    
    """
    Measure the counts for a range of wavelengths, output an xlsx file for each wavelength
    Measure the power in the reference arm during the measurements, output a final xlsx file with the fluctuations
    
    INPUT:
        tcp_ip_address (STR)
        control_port (INT)
        counts_port (INT)
        N = number of counts per measurement
        number_of_detectors (INT)
        Ib = list of bias currents
        waves = list of wavelengths to measure on (LIST)
        db = a set attenuation level (INT)
        laserip (STR)
        laserchannel (INT) 
    """
    
    from ctypes import c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_double,c_int16
    from TLPM import TLPM 
    import laser
    import Attenuator
    import time
    
    l = laser.Laser()
    l.open_port(laserip,laserchannel) # connects
    
    d = Attenuator.Attenuator()
    d.open_port('192.168.1.148','18')
    
    tlPM = TLPM()
    resourceName1 = create_string_buffer(10240)
        
    deviceCount = c_uint32()
    tlPM.findRsrc(byref(deviceCount))
    for i in range(0, deviceCount.value):
        tlPM.getRsrcName(c_int(i), resourceName1)
        
    # create a df each column containing the efficiency of all detectors per wavelength
    df2 = pd.DataFrame(columns = waves)    
        
    pf = pd.DataFrame(columns = waves)

    for wave in waves:

        l.setWVL(wave)
        d.setAtt(db)    
        d.setWVL(wave)
        
        print("================================")
        print("The wavelength is now set to:",l.getWVL())

        j=0
        time.sleep(10) # let it calibrate
        #set wavelength power meter
        tlPM.open(resourceName1, c_bool(True), c_bool(True))
        # set wavelength
        waveset =  c_double(wave)
        tlPM.setWavelength(waveset)
        
        print(tlPM.setWavelength(waveset))
        print(waveset.value)
        
        time.sleep(1)
        power_fluct = np.zeros(10)            
            
        while j<10:
            
            power =  c_double()
            tlPM.measPower(byref(power))
        
            print(power.value)
        
            p = power.value        
            
            power_fluct[j]=p
            time.sleep(0.5)
            print(p)
            
            j = j+1
        tlPM.close() 
        
        power_fluct2=power_fluct[3:]
        p = np.average(power_fluct2)
        print(p)
        
        # get detected counts of the SNSPD system, only average counts of N measurements for all detectors
        SNSPD_counts = detected_counts(tcp_ip_address, control_port, counts_port,N, number_of_detectors, Ib, wave)[0].tolist()
        print(SNSPD_counts)
        
        df2[wave]=SNSPD_counts
        pf[wave] = power_fluct
        
    # drop first row containing timestamps
    df2 = df2.iloc[1:,:]
    df2.to_excel("measurements.xlsx")
 
    pf = pf.iloc[1:,:]
    pf.to_excel("powerfluctuationsf.xlsx")
    print(df2)
    print(pf)
    
    return df2, pf

def setattenuator(db,wav):
    """
    This function sets the attenuation and the wavelength for the attenuator
    
    INPUT:
        db = the attenuation level in db, INT
        wav = the wavelength in nm, INT
    """
    import Attenuator
    
    d = Attenuator.Attenuator()
    d.open_port('192.168.1.148','18')
    d.setAtt(db)    
    d.setWVL(wav)