#!/usr/bin/env python2.6


# reads memory locations written to by a Lua script running on the labjack

from labjack import ljm
import time
# Open first found LabJack
# see https://labjack.com/support/software/api/ljm/function-reference/ljmopen

handle = ljm.openS("ANY", "ANY", "ANY")

# Call eReadName to read the serial number from the LabJack.
name = "SERIAL_NUMBER"
result = ljm.eReadName(handle, name)
result = ljm.openS("T7", "ANY", "My_T7_5741")

print("\neReadName result: ")
print("    %s = %f" % (name, result))

counter = 0
#46000

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))


while 1:
  for address in [46000, 46002, 46004, 46006]:
    # Setup and call eReadAddress to read a value from the LabJack.
    dataType = ljm.constants.UINT32
    result = ljm.eReadAddress(handle, address, 3)

    print("%i    Address - %i, value : %f" %  (counter, address, result))

  result = ljm.eReadAddress(handle, 60050, 3) - 273.15  # also read internal temperature and convert from K to C
  print "--------------\n{:.1f} C\n------------\n".format(result )
  time.sleep(10)
  counter+=1


# Close handle
ljm.close(handle)
