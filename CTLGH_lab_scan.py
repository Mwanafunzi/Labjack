#!/usr/bin/env python



#reads database to show health of the CTLGH lab by means of google charts

import MySQLdb
import time
import MySQLdb.cursors
import json


db_host = "localhost"
db_user = "root"
db_passwd = "IceCream!"



#######################################################  #####
# connect to the MySQL server
def connect2db():
  global conn
  while 1:
      try:
 #       print "Connecting to database..."
    conn = MySQLdb.connect ( host = db_host, user = db_user, passwd = db_passwd, cursorclass=MySQLdb.cursors.DictCursor)
    conn.autocommit(True)
    break
      except MySQLdb.Error, e:
    #print "Error %d: %s. Sleeping for 5 seconds before trying again." % (e.args[0], e.args[1])
    time.sleep(5)

############################  #############

connect2db()
cursor = conn.cursor ()


sql = 

