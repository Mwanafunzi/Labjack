#!/usr/bin/env python2.6


# reads memory locations written to by a Lua script running on he labjack



#uses the "Deep Search" function for searching explicit IP ranges. 
# The config file lives here:
# /usr/local/share/LabJack/LJM/ljm_deep_search.config
#And there are instructions about the IP syntax here:
# https://labjack.com/support/software/api/ljm/constants/DeepSearchConfigs


from labjack import ljm
import time
# Open first found LabJack
counter = 0


reads = {'1TopPressure': 'AIN2', '2Av top P':'AIN2_EF_READ_A', '3BottomPressure': 'AIN0',  
         '4Av bottom P':'AIN0_EF_READ_A', '5_O2': 'AIN4',  'shutoff': 'DIO0', 'door': 'DIO1', 
         'plant': 'DIO2', 'vent alarm': 'DIO5', 'vent valve': 'DIO6', 'fillpoint':'AIN6'}


while 1:
  #handle = ljm.openS("ANY", "ANY", "172.26.18.211") 
  #handle = ljm.openS("ANY", "ANY", "470013413") 
  #172.26.15.248
  handle = ljm.openS("ANY", "ANY", "CTLGH_ReproLab_T7")  

# ser no 470015143 is cremator on 172.26.15.248
#   Serial number: 470015097, IP address: 172.26.19.238 -80 freezer on 172.26.19.238
# Serial number: 470013413, IP address: 172.26.18.211  Incinerator_T7 
# CTLGH_ReproLab_T7 serial number 470015741. use DHCP 
# Biorepository_T7 serial number 470015750 Use DHC



# Call eReadName to read the serial number from the LabJack.
  name = "SERIAL_NUMBER"
  result = ljm.eReadName(handle, name)
  result = ljm.openS("T7", "ANY", "ANY")



#set up averaging
  """
  ljm.eWriteName(handle, 'AIN0_EF_INDEX', 3)
  ljm.eWriteName(handle, 'AIN0_EF_CONFIG_A', 50) #no of samples
  ljm.eWriteName(handle, 'AIN0_EF_CONFIG_D', 1000) #scan rate


  ljm.eWriteName(handle, 'AIN2_EF_INDEX', 3)
  ljm.eWriteName(handle, 'AIN2_EF_CONFIG_A', 50)
  ljm.eWriteName(handle, 'AIN2_EF_CONFIG_D', 1000)""" 

  info = ljm.getHandleInfo(handle)
  print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


  #for address in [0,  2,  4, 6, 8, 46000, 46002, 46004, 46006, 7000, 7001, 7002, 7003, 7004]:
  #for address in [0,  2,  4, 6, 8, 46000, 46002, 46004, 46006, 7000, 7300, 7600, 7004, 7304, 7604]:
  #for address in [0, 4, 8, 2000, 2001, 2002, 2005, 2006]:
  #for item in sorted(reads.keys()):
  for address in [46000, 46002, 46004, 46006]:

    #address = reads[item]
    # Setup and call eReadAddress to read a value from the LabJack.
  

    result = ljm.eReadAddress(handle, address, 3)
    print address, result

  string = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")


  print "--------------\n{}\n------------\n".format(string )

  #ljm.eWriteNameString(handle, "DEVICE_NAME_DEFAULT", "CTLGH_-80_T7")

  counter+=1

  # Close handle
  ljm.close(handle)
  time.sleep(5)

