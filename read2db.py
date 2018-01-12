#!/usr/bin/env python2.6

import MySQLdb
import time
import MySQLdb.cursors
import json


db_host = "localhost"
db_user = "root"
db_passwd = "IceCream!"

sleep_time = 10*60
address_list = [46000, 60050]


#######################################################  #####
# connect to the MySQL server
def connect2db():
  global conn
  conn = MySQLdb.connect ( host = db_host, user = db_user, passwd = db_passwd, cursorclass=MySQLdb.cursors.DictCursor)
  conn.autocommit(True)
############################  #############

connect2db()
cursor = conn.cursor ()



# reads memory locations written to by a Lua script running on the labjack

from labjack import ljm
import time
# Open first found LabJack
# see https://labjack.com/support/software/api/ljm/function-reference/ljmopen

handle = ljm.openS("ANY", "ANY", "ANY")


counter = 0
#46000

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


while 1:
  #for address in [46000, 46002, 46004, 46006]:
  for address in address_list:
    # Setup and call eReadAddress to read a value from the LabJack.
    dataType = ljm.constants.UINT32
    try:
       result = ljm.eReadAddress(handle, address, 3)
       if address == 60050:
         result = result  - 273.15

       print("%i    Address - %i, value : %f" %  (counter, address, result))
       sql = """INSERT INTO freezers.`sensor_readings` ( `device`, `reading`, `recorded`) VALUES  ({a}, {r}, NOW() ) ;""".format( a = address, r =result)

    except:
      print "Failed to read from LJ or write to db"
  

    cursor.execute(sql)
  print
  time.sleep(sleep_time)
  counter+=1






# Close handle
ljm.close(handle)
