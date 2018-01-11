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
  global dict_conn

  dict_conn = MySQLdb.connect ( host = db_host, user = db_user, passwd = db_passwd, cursorclass=MySQLdb.cursors.DictCursor)
  conn = MySQLdb.connect ( host = db_host, user = db_user, passwd = db_passwd)

############################  #############

connect2db()
cursor = conn.cursor ()
dict_cursor = dict_conn.cursor ()



sql = """select concat("Date(",Year(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Month(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Day(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Hour(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Minute(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Second(DATE_SUB(recorded, INTERVAL 3 HOUR)) , ")") as fdat,
reading
 from freezers.sensor_readings where device = 46000 order by recorded desc"""



cursor.execute(sql)
plot_data = cursor.fetchall()
dust_plot_json = json.dumps(plot_data)




sql = """select concat("Date(",Year(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Month(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Day(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Hour(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Minute(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Second(DATE_SUB(recorded, INTERVAL 3 HOUR)) , ")") as fdat,
reading
 from freezers.sensor_readings where device = 60050 order by recorded desc"""
cursor.execute(sql)
plot_data = cursor.fetchall()
temp_plot_json = json.dumps(plot_data)



print """Content-Type: text/html

<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawDustChart);
      google.charts.setOnLoadCallback(drawTempChart);



  var dust_dat  = %s
  dust_dat.unshift([ {type: 'datetime'}, 'Dust level'])

      function drawDustChart() {
        var data = google.visualization.arrayToDataTable(dust_dat);

        var options = {
          title: 'Dust levels (>1 micron) measured by Shinyei PPD42NJ',
          hAxis: {title: 'Date/time'},
          vAxis: {title: 'Dust'},
          legend: 'none'
        };

        var chart = new google.visualization.LineChart(document.getElementById('dust_div'));

        chart.draw(data, options);
      }



  var temp_dat  = %s
  temp_dat.unshift([ {type: 'datetime'}, 'Temperature'])

     function drawTempChart() {
        var data = google.visualization.arrayToDataTable(temp_dat);

        var options = {
          title: 'Temperature',
          hAxis: {title: 'Date/time'},
          vAxis: {title: 'Temperatue deg C'},
          legend: 'none'
        };

        var chart = new google.visualization.LineChart(document.getElementById('temp_div'));

        chart.draw(data, options);
      }




    </script>
  </head>
  <body>
    <div id="dust_div" style="width: 900px; height: 500px;"></div>
    <div id="temp_div" style="width: 900px; height: 500px;"></div>

  </body>
</html>

""" % (dust_plot_json, temp_plot_json)





