#!/usr/bin/env python


#reads T7 labjacks using deep search method

# Needs JackPython: http://github.com/labjack/LabJackPython

#uses the "Deep Search" function for searching explicit IP ranges. 
# The config file lives here:
# /usr/local/share/LabJack/LJM/ljm_deep_search.config
#And there are instructions about the IP syntax here:
# https://labjack.com/support/software/api/ljm/constants/DeepSearchConfigs

import MySQLdb
import time
import MySQLdb.cursors

import LN2config

write_interval = 30*60
sleep_time = 0.10*60
connect_wait_time = 10

write_time = 0

#######################################################  #####
# connect to the MySQL server
def connect2db():
  global conn
  conn = MySQLdb.connect ( host = LN2config.db_host, user = LN2config.db_user, passwd = LN2config.db_passwd, db = LN2config.db_db, cursorclass=MySQLdb.cursors.DictCursor)
  conn.autocommit(True)
############################  #############

db_cnxn = 0
while not db_cnxn:
  try:
    connect2db()
    cursor = conn.cursor ()
    db_cnxn = 1
  except:
    print "failed to connect to ",LN2config.db_db,"on", LN2config.db_host
    time.sleep(connect_wait_time)


# reads memory locations written to by a Lua script running on the labjack

from labjack import ljm
import time
# Open first found LabJack
# see https://labjack.com/support/software/api/ljm/function-reference/ljmopen



write_loop = 0
last_temp = {}

### get a list of T7's addressed by name. ie where talkbox contains 't7' and ip is not a valid ip  
while 1:

   write_loop =   time.time() - write_time >  write_interval    

   sql = """SELECT ip as name, description, unitid, port_name,  temperature_wobble from freezer_units
          where in_use >0 and talkbox like '%T7' and INET_ATON(ip) IS  NULL order by ip;"""
   
   count = 0
   not_got = 1
   while not_got:
      try:
        cursor.execute (sql)
        not_got = 0
      except e:
        print count, "Failed to get device list. Will keep trying",e
        count+=1
        time.sleep(connect_wait_time)



   open_device = ''
   for sensor in cursor.fetchall():
      if open_device <> sensor['name'] and open_device <> '':   #new labjack and not 1st run
        try:
          ljm.close(handle)
        except:
          print "Failed to close ", open_device
        print 'closed..', open_device

     #print "Labjack", sensor['name'],
 
      try:

          handle = ljm.openS("ANY", "ANY", sensor['name']) ## no problem if its already open LJM will know this and make instamnt cnxn  
          info = ljm.getHandleInfo(handle)
          open_device = sensor['name']
          print "   LabJack {} serial #: {}, ip {} ".format( sensor['name'], info[2],  ljm.numberToIP(info[3])),

          address = sensor['port_name']

          #result = ljm.eReadName(handle, address)
          #result = ljm.eReadAddress(handle, address, 3)
          result = ljm.eReadName(handle, address)

          this_unit = sensor['unitid']

          if address == 'TEMPERATURE_AIR_K':
            result = result  - 273.15
          #exit()
          print("Sensor id: {} Address: {}, value : {:.1f}".format(this_unit, address, result))

          if this_unit in last_temp:    # if we  have a last_temp
             wobbly = (abs(result -  last_temp[this_unit]) >= sensor['temperature_wobble'])
             #print "Result", result,"last temperature", last_temp[this_unit], "wobbl is", abs(result -  last_temp[this_unit]),"this is ", wobbly
          else:
              wobbly = False

          if write_loop or wobbly:
            sql = """INSERT INTO `freezer_log` ( `freezer`, `created`, `temp`) VALUES({a}, now(), {r});""".format( a = this_unit, r =result)

            print 'writing to db'
            if wobbly:
              print '   **** wobble **** of {:.1f}'.format(abs(result -  last_temp[this_unit]))
            try:
              cursor.execute(sql)
              if not wobbly:
                write_time = time.time() #leave the normal write time unchanged - don't start a new delay from a wobble-triggered write
              last_temp[this_unit] = result
            except Exception, e:
              print e


      except Exception, e:
         print "Failed to read from LJ or write to db",e
   time.sleep(sleep_time)
 
