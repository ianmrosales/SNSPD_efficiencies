import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def count_rate_plotter(avgscounts, xIb, number_of_detectors):
    """
    Plot the count rate for different currents
    
    INPUT:
        avgscounts = nested LIST of counts
        xIb = LIST of currents for x-scale
        number_of_detectors (INT)           
    """
    for k in range(0, number_of_detectors):
        newlist = []
        for i in range(k, len(avgscounts), 8):
            newlist.append(avgscounts[i])
            
        plt.title("Count rate vs I_bias")    
        plt.plot(xIb, newlist,label = "Detector "+str(k+1))  
        plt.legend()
    plt.show()
    plt.savefig("countrate.png")
    plt.close()

def plot_efficiency(xIb, efficiency, number_of_detectors):
    """
    Plot the efficiency for each detector as a function of a range of currents
    
    INPUT:
        xIb = range of currents for x-scale, LIST
        efficiency =  LIST
        number_of_detectors = INT
    """  
    for k in range(0, number_of_detectors):
        newlist = []
        for i in range(k, len(efficiency), 8):
            newlist.append(efficiency[i])
            
        plt.title("Efficiency vs I_bias")    
        plt.plot(xIb, newlist,label = "Detector "+str(k+1))  
        plt.legend()
    plt.show()
    plt.savefig("eff.png")
    plt.close()
    

def wavelength_plot(waves_list, waves,number_of_detectors):
    """
    This function plots the measured efficiency for different wavelengths
    
    INPUT:
        waves_list = LIST containing a range of wavelengths
        waves = LIST containing a range of wavelengths
        number_of_detectors = INT
    """
    
    for k in range(0, number_of_detectors):
        newlist = []
        for i in range(k, len(waves_list), 8):
            newlist.append(waves_list[i])
            
        print(newlist) 
        print(len(newlist))
        plt.title("Efficiency vs wavelength")    
        plt.plot(waves, newlist,label = "Detector "+str(k+1))  
        plt.legend()
        
    plt.show()
    plt.savefig("wavelength_eff.png")
    plt.close()

# functions to plot the power of the laser 
def power_plotter(df, times):  

    """
    Plot the measured power per wavelength, in separate graph
    
    INPUT:
        df = DataFrame containing all power measurements, sorted per wavelength
        times = LIST of times for x-scale of the plot
    """         
    # calculate std deviation of each column and determine its fluctuations
    for header in df:
        array = df[header].to_numpy()
        array = [i*10**3 for i in array]
        # make nice plot power fluctuations
        plt.plot(times, array, linestyle = "solid", marker = "*",label = str(header)+" nm")
        plt.xlabel("Time (s)")
        plt.ylabel("Power (mV)")
        plt.title("Stability test Power fluctuation")
        plt.legend()
        plt.savefig("powerfluct"+str(header)+".png")
        plt.show()
        plt.close()

def totpower_plotter(df, times):   

    """
    Plot the measured power per wavelength, in one figure
    
    INPUT:
        df = DataFrame containing all power measurements, sorted per wavelength
        times = LIST of times for x-scale of the plot
    """          
    
    # calculate std deviation of each column and determine its fluctuations
    for header in df:
        array = df[header].to_numpy()
        array = [i*10**3 for i in array]
        # make nice plot power fluctuations
        plt.plot(times, array, linestyle = "solid", marker = "*",label = str(header)+" nm")
    plt.xlabel("Time (s)")
    plt.ylabel("Power (mV)")
    plt.title("Stability test Power fluctuation")
    plt.legend()
    plt.savefig("powerflucttot.png")
    plt.show()
    plt.close()

def laser_stability_plot(df, waves):
    """
    THIS FUNCTION OUTPUTS A GRAPH SHOWING THE LASER STABILITY FOR ALL WAVELENGTHS

    Parameters
    ----------
    df : dataframe, excel file
        DATAFRAME CONTAINING ALL THE LASER STABILITY DATA.
    waves : array
        ARRAY CONTAINING ALL CORREPONDING WAVELENGTGHS.

    Returns
    -------
    None.

    """
    data = pd.DataFrame()
    averages = []
    deviations = []
    for header in df:
        array = df[int(header)].to_numpy()
        array = [i*10**3 for i in array]
        
        averages.append(np.average(array))
        deviations.append(np.std(array))
    
    # make nice plot power fluctuations
    #plt.plot(waves, averages, linestyle = "solid", marker = "*")

    plt.errorbar(waves, averages, yerr = deviations)
    plt.xlabel("wavelengths (nm)")
    plt.ylabel("Power (mW)")
    plt.title("Laser power")
    plt.savefig("powerfluct"+str(header)+".png")
    plt.grid()
    plt.show()
    plt.close()
    
    perc = [deviations[i]/averages[i] for i in range(len(averages))]
    
    data["averages"]= averages
    data["std deviations"] = deviations
    data["%"] = perc
    data.index = ([i for i in df])
    data.to_excel("plot_data.xlsx")
    
    return averages, deviations, perc, data
        
def stability_plotter(df, waves):
    """
    Plot stability of the power for every wavelength
    
    INPUT:
        df = DataFrame containing all power measurements, sorted per wavelength
        waves = LIST of wavelengths for x-scale of the plot
    """
    stability = []
    for header in df:
        array = df[header].to_numpy()

        std_dev = np.std(array)
        average = np.average(array)
        stability.append(std_dev/average) 
    
    # nice plot for stability, how it changes per wavelength
    plt.plot(waves, stability)   
    plt.title("Stability per wavelength")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Stability")
    plt.savefig("stability.png")
    plt.show()
    plt.close()    
    
    return stability    

def measurements_plotter(counts_meas, laspower, times, number_of_detectors):
    """
    Plot the laser power???
    """
    
    # plot laser power during time of measurement
    plt.plot(times, laspower)
    plt.xlabel("time (s)")
    plt.ylabel("power")
    plt.title("Power course during measurements")
    plt.savefig("powerduringmeasurement.png")
    plt.show()
    plt.close()
    
    #probably have to remove column/row for timestamps counts_meas
    for i in range(number_of_detectors):
        array = counts_meas.iloc[ : , i+1 ].to_numpy()#correct for timestamp
        plt.plot(times,array,label= "Detector "+str(i+1))
    plt.xlabel("time (s)")
    plt.ylabel("counts")
    plt.legend()
    plt.title("counts per detector over time")
    plt.savefig("countstime.png")
    plt.show()
    plt.close()
    
def getratios2(df1, df2):
    """
    Calculate the ratios between the measured powers from the two powermeters for each wavelength
    
    INPUT:
        df1 = DataFrame 1 for power meter 1, reference arm
        df2 = DataFrame 2 for power meter 2, measurement arm
    
    OUTPUT:
        ratios = LIST containing the ratios between the measured power meters
        dbratios = LIST containing the dbratios between the measured power meters
    """
    
    ratios = []
    dbratios = []
    
    ratiosdf = pd.DataFrame()
    av1 = []
    av2 = []
    for header1 in df1:

        avg1 = np.average(df1[header1].to_numpy()[2:]) #first few measurements are bad
        avg2 = np.average(df2[header1].to_numpy()[2:])
        
        ratio = np.abs(avg1/avg2)

        dbratio = 10*np.log10(ratio)
        av1.append(avg1)
        av2.append(avg2)
        dbratios.append(dbratio) # error check code
        ratios.append(ratio)
    ratiosdf["Average P1"]=av1
    ratiosdf["Average P2"]=av2
    ratiosdf["Ratios"]=ratios 
    ratiosdf["dB ratios"] = dbratios
    ratiosdf.index = ([i for i in df1])
    ratiosdf.to_excel("ratios.xlsx")
    return ratios, dbratios

def ploteffwav(waves, efficiency, i):
    plt.plot(waves, efficiency*100, marker = ".", linestyle="solid", label = "Measurement "+str(i+1))
    plt.title("Efficiency vs wavelength")
    plt.xlabel("Wavelengths (nm)")
    plt.ylabel("Efficiency (%)")
    plt.legend()
    plt.grid()
    plt.savefig("Efficiency.png")
    
      
def photon_eff(wav, ratios, pwrs, number_of_detectors, detected_counts, j):
    """ 
    This function calculates the efficiency of the system for a range of wavelenghts 
    
    - The total number of photons is calculated using the given input power pwrs (LIST) of the reference
    arm, attenuated to get the power input for the SNSPD.
    
    - Ratios is a list containing the ratios for the measurement arm and the reference arm, respectively, for all wavelengths
    
    - The detected_counts is the list of (avg) counts corresponding with the list of powers, respectively
    
    INPUT:
        wav = wavelength in nanometer (LIST)
        ratios = ratio between arm and measurement arm for the range of wavelengths ~ 50dB (LIST)
        pwrs = measured power in reference arm (LIST)
        number_of_detectors = INT
        detected_counts = LIST
        j = number for naming
        
    """
    analysis = pd.DataFrame()
    p=[]
    for i in pwrs[1:]:
        array = pwrs[i].to_numpy()
        pi = np.average(array)
        p.append(pi)
    p = p[1:]

    totalp = []
    index = int((wav[0]-1260)/10) # correct for the right domain in the ratios array
    for i in range(len(p)):
        totalp.append(p[i]/ratios[i+index])

    # calculate energy per photon
    h = 6.62607015*10**(-34) 
    c = 299792458
    Ewav = [h*c/(i*10**-9) for i in wav]
    
    # Calculate the total amount of photons
    # assumes power meter is before attenuator, hence it reduces signal
    total_photons = [totalp[i]/Ewav[i] for i in range(len(totalp))]
    
    # get the efficiency for every measurement for every detector
    efficiency = np.zeros(len(detected_counts))

    for i in range(len(detected_counts)):
        efficiency[i] = detected_counts[i]/total_photons[i]
    
    analysis["System Power"] = totalp
    analysis["Total Photon count"] = total_photons 
    analysis["Measured Photon count"] =   detected_counts     
    analysis["Efficiency"] = efficiency
    analysis.index = ([i for i in wav])
    analysis.to_excel("analysis"+str(wav[0])+"V"+str(j+1)+".xlsx")
    
    return total_photons, efficiency