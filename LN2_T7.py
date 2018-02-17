#!/usr/bin/env python2.6

# gets LN2-related information from a specific labjack

# labjack is set to use extended function for average values from AIN0, AIN2 and AIN4.
# THese AIN's are also set to use signal as positive and adjacent channel as negative.

#uses the "Deep Search" function for searching explicit IP ranges. 
# The config file lives here:
# /usr/local/share/LabJack/LJM/ljm_deep_search.config
#And there are instructions about the IP syntax here:
# https://labjack.com/support/software/api/ljm/constants/DeepSearchConfigs

import time
import datetime

import MySQLdb
import MySQLdb.cursors

from labjack import ljm
# Open the labjack LabJack


import LN2config


write_interval = 30*60
sleep_time = 25
connect_wait_time = 10

write_time = 0

read_channels = {
         '1TopPressure':         'AIN2',           # raw pressure input at the AIN. Actually ignored
         '2Average_top_P':       'AIN2_EF_READ_A', # average using EF. This will be the the value used
         '3BottomPressure':      'AIN0',           # raw input at the AIN. Actually ignored
         '4Average_bottom_P':    'AIN0_EF_READ_A', # average pressure using EF. This will be the the value used
         'raw4':                 'AIN4',
         '5_O2':                 'AIN4_EF_READ_A',           # oxygen level is this reading * 10
         'shutoff':              'DIO0', 
         'door':                 'DIO1', 
         'plant':                'DIO2', 
         'vent_alarm':           'DIO5', 
         'vent_valve':           'DIO6', 
         'fillpoint':            'AIN6', 
         'ambient':              'TEMPERATURE_AIR_K',
         'fan_0':                'DAC0',
         'fan_1':                'DAC1'}


#######################################################  #####
# connect to the MySQL server
def connect2db():
  global conn
  conn = MySQLdb.connect ( host = LN2config.db_host, user = LN2config.db_user, passwd = LN2config.db_passwd, db = LN2config.db_db, cursorclass=MySQLdb.cursors.DictCursor)
  conn.autocommit(True)
############################  #############

def retry_cnct():   # loop to allow repeatred retries of cnxn. Why not built into connect_2db?
  db_cnxn = 0
  global cursor

  while not db_cnxn:
    try:
      connect2db()
      cursor = conn.cursor ()
      db_cnxn = 1
    except Exception, e:
      print "failed to connect to ",LN2config.db_db,"on", LN2config.db_host, e
      time.sleep(connect_wait_time)

############################  #############


while 1:

  retry_cnct()

  write_loop =   time.time() - write_time >  write_interval    
  read_ok = 1

  try:
    handle = ljm.openS("ANY", "ANY", "Biorepository_T7")  
    #info = ljm.getHandleInfo(handle)

    devicename = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
    ts = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    #print "\nLabjack {} serial # {} found on ip {} at {}\n-----------".format(devicename, info[2], ljm.numberToIP(info[3]), ts )
    print "\nLabjack {}  at {}\n-----------".format(devicename,  ts )

    resultset = {}
    for item in sorted(read_channels.keys()):
      address = read_channels[item]
  
      result = ljm.eReadName(handle, address)

      if 'fillpoint' in item:
        result =  (55.56*result) + 255.37 - 273.15

      elif 'fans'  in item:
        result = result < 3.5

      elif 'Average' in item:
         result *=  1000

      elif 'O2' in item:
         result *=  10

      elif 'ambient' in item:
         result -= 273.15

      elif 'plant' in item:
          result = not result # flip state
       
      resultset[item] = result   #accumulate results in a dictionary

      print " {:20} {:25} {:6.4f}".format(item, address, result)
  except Exception, e:
    print 'failed to acces labjack', e
    read_ok = 0



  #compare_results(resultset, last_resultset)   # look for difference requiring a write
  
  if write_loop and read_ok:
       sql = """INSERT INTO `pressure` ( `analog0`, `analog1`, `O2`, `switch`, `fill_point`, `ambient`, `door`, `LN2_plant`, `fan_0`, `fan_1`, `cause`, `timestamp`, `vent_valve`, `vent_alarm`)
             VALUES
            ( {2Average_top_P}, {4Average_bottom_P}, {5_O2}, {shutoff}, {fillpoint}, {ambient}, {door}, {plant}, {fan_0}, {fan_0}, 'Time', now(), {vent_valve}, {vent_alarm});""".format(**resultset)  
  
  
       print '**** writing to db....', 
       try:
         cursor.execute(sql)
         write_time = time.time() 
         last_resultset = resultset   # remember what we just wrote
         print '....ok'
       except Exception, e:

         # write failed. Assume that mysql cnxn is down
         # start retrying it

         print e, 'retrying cnxn'
         retry_cnct()

  

  # Close handle
  try:
    ljm.close(handle)
  except:
    print 'failed to close labjack'
  cursor.close()
  time.sleep(sleep_time)

