#!/usr/bin/env python2.6

# gets LN2-related information from a specific labjack


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
sleep_time = 5
connect_wait_time = 10

write_time = 0

read_channels = {
         '1TopPressure':         'AIN2',           # raw pressure input at the AIN. Actually ignored
         '2Average top P':       'AIN2_EF_READ_A', # average using EF. This will be the the value used
         '3BottomPressure':      'AIN0',           # raw input at the AIN. Actually ignored
         '4Average bottom P':    'AIN0_EF_READ_A', # average pressure using EF. This will be the the value used
         '5_O2':                 'AIN4',           # oxygen %. actually V * 10
         'shutoff':              'DIO0', 
         'door':                 'DIO1', 
         'plant':                'DIO2', 
         'vent alarm':           'DIO5', 
         'vent valve':           'DIO6', 
         'fillpoint':            'AIN6', 
         'fans1':                'DAC1',
         'ambient':              'TEMPERATURE_AIR_K'}


#######################################################  #####
# connect to the MySQL server
def connect2db():
  global conn
  conn = MySQLdb.connect ( host = LN2config.db_host, user = LN2config.db_user, passwd = LN2config.db_passwd, db = LN2config.db_db, cursorclass=MySQLdb.cursors.DictCursor)
  conn.autocommit(True)
############################  #############

def retry_cnct():   # loop to allow repeatred retries of cnxn. Why not built into connect_2db?
  db_cnxn = 0
  while not db_cnxn:
    try:
      connect2db()
      cursor = conn.cursor ()
      db_cnxn = 1
    except Exception, e:
      print "failed to connect to ",LN2config.db_db,"on", LN2config.db_host, e
      time.sleep(connect_wait_time)

    return cursor
############################  #############


while 1:

  cursor = retry_cnct()

  write_loop =   time.time() - write_time >  write_interval    

  try:
    handle = ljm.openS("ANY", "ANY", "Biorepository_T7")  
    #info = ljm.getHandleInfo(handle)

    devicename = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
    ts = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")

    #print "\nLabjack {} serial # {} found on ip {} at {}\n-----------".format(devicename, info[2], ljm.numberToIP(info[3]), ts )
    print "\nLabjack {}  at {}\n-----------".format(devicename,  ts )

    ljm.eWriteName(handle, 'DAC1', 4.5)

    resultset = {}
    for item in sorted(read_channels.keys()):
      address = read_channels[item]
  
      result = ljm.eReadName(handle, address)

      if 'fillpoint' in item:
        result =  (55.56*result) + 255.37 - 273.15

      elif 'fans1'  in item:
        result = result < 3.5

      elif 'Average' in item:
         result *=  1000

      elif 'O2' in item:
         result *=  10
      elif 'ambient' in item:
         result -= 273.15
       
      resultset[item] = result   #accumulate results in a dictionary

      print " {:20} {:25} {:6.4f}".format(item, address, result)
  except:
    print 'failed to acces labjack'


  #compare_results(resultset, last_resultset)   # look for difference requiring a write
  
  if write_loop:
       sql = """INSERT INTO `pressure` ( `analog0`, `analog1`, `O2`, `switch`, `fill_point`, `ambient`, `door`, `LN2_plant`, `fans_status`, `cause`, `timestamp`, `vent_valve`, `vent_alarm`)
             VALUES
            ( {2Average top P}, {4Average bottom P}, {5_O2}, {shutoff}, {fillpoint}, {ambient}, {door}, {plant}, {fans1}, 'Time', now(), {vent valve}, {vent alarm});""".format(**resultset)  
  
  
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
         cursor = retry_cnct()

  

  # Close handle
  try:
    ljm.close(handle)
  except:
    print 'failed to close labjack'
  cursor.close()
  time.sleep(5)

