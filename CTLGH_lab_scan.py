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

dust_plot_json = {} #hold jsons for each device
js_str = ''
div_str = ''


#get list of devices


sql = "select * from freezers.sensor_list where in_use = 1 group by device order by device ;"
dict_cursor.execute(sql)
sensor_list = dict_cursor.fetchall()
for  row_dict in sensor_list:
  

   sql = """select concat("Date(",Year(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Month(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Day(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Hour(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Minute(DATE_SUB(recorded, INTERVAL 3 HOUR)), ", ", Second(DATE_SUB(recorded, INTERVAL 3 HOUR)) , ")") as fdat,
             reading
             from freezers.sensor_readings where device = {dev} and recorded >= DATE_SUB(now(), INTERVAL {d} DAY) order by recorded desc """.format(dev = row_dict['device'], d = row_dict['plot_days'])



   n = cursor.execute(sql)
   plot_data = cursor.fetchall()
   #dust_plot_json[row_dict['device']] = json.dumps(plot_data)


   if n > 1:

      js_str+= """   


      google.charts.setOnLoadCallback(draw{dev}Chart);


      function draw{dev}Chart() {{

        var dust_dat  = {dat}

        dust_dat.unshift([ {{type: 'datetime'}},'{y}'])

        var data = google.visualization.arrayToDataTable(dust_dat);

        var options = {{
          title: '{title}',
          hAxis: {{ title: '{x}' }},
          vAxis: {{ title: '{y}'}},
          legend: 'none'
        }};

        var chart = new google.visualization.LineChart(document.getElementById('{dev}_div'));

        chart.draw(data, options);
      }}



      """.format( dev = row_dict['device'], dat=json.dumps(plot_data), x = row_dict['x-axis_title'], y = row_dict['y-axis_title'], title = row_dict['plot_title'] )


      div_str += """  
               <div id="{dev}_div" style="width: 900px; height: 500px;"></div>
               """.format(dev = row_dict['device'])


print """Content-Type: text/html

<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});




%s

 




    </script>
  </head>
  <body>
    

%s

  </body>
</html>

""" % (js_str, div_str)





