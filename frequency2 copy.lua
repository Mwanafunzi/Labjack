
-- counting pulses to get the frequency of the hall effect sensor
-- https://labjack.com/pages/support?doc=%2Fsoftware-driver%2Flabjack-applications%2Fconfiguring-reading-a-counter%2F
-- https://labjack.com/pages/support?doc=%2Fapp-notes%2Fdigital-io-app-note%2Fopen-collector-signals-app-note%2F
-- count pulses from 2 simple NPN hall effect flow meters
-- red, black to Vs gnd, Yellow to FIO0/1 for each device
-- a 6.6K pull up resister between Vs and signal
-- Data saved to user space for collection by a python script

-- this requires we use core clock ticks
-- v3 modified so that rather than sleeping, we use the core timer for time interval so we can do other stuff especially flashing the LEDs to convey information while accumulating counts


local pulses = 0
local sensor = 0
local window =   0
local Q = 5.5 -- factor to convert Hz to litres per minute
local op      -- output string holder
local timerID = 7 -- which timer to use
local TicksPerSec = 40*1000*1000 -- core clock ticks per second ONLY APPLIES TO t7 and T4 NOT T8 or others

-- For sections of code that require precise timing assign global functions
-- locally (local definitions of globals are marginally faster)

local results_storage = {}
results_storage[0] = 'USER_RAM0_F32' -- where we put our data to be collected by python script which periodically scans all labjacks
results_storage[1] = 'USER_RAM1_F32' -- a bit clumsy as Lua arrays start at 1 by defauilt


function sleep(time_ms)
    LJ.IntervalConfig(6, time_ms)  
    while( LJ.CheckInterval(6) ~= 1 )do
    end
end


function LED_flash(times) -- flash both LEDs together this many times
    local i = 0
  local numiterations = times * 2
  -- Set the LED operation to manual 
  MB.writeName("POWER_LED", 4)
  
  MB.writeName("LED_COMM", 0) -- start with both off
  MB.writeName("LED_STATUS", 0)
  local ledstatus = 0
  sleep(2000)
  
  -- Configure a flash interval
  LJ.IntervalConfig(0, 500)

  while i < numiterations do
    if LJ.CheckInterval(0) then
      ledstatus = 1 - ledstatus -- that's clever. neater than if then else!
      MB.writeName("LED_COMM", ledstatus)
      MB.writeName("LED_STATUS", ledstatus)
      i = i + 1
    end
  end

  MB.writeName("LED_COMM", 0) -- end with both off
  MB.writeName("LED_STATUS", 0)

  sleep(2000)

end


  
error = MB.writeName("LUA_NO_WARN_TRUNCATION", 1)

-- set up counters
for sensor = 0, 1, 1 do -- set up DAC0 and 1
  MB.writeName(string.format("DIO%.0f_EF_ENABLE", sensor), 0) -- disable as cannot change index if enabled.
  MB.writeName(string.format("DIO%.0f_EF_INDEX", sensor),8) -- dunno what that does
  MB.writeName(string.format("DIO%.0f_EF_ENABLE", sensor), 1) -- Re-enable.
end


while 1 do
  -- get the core clock counts as soon as we enter the loop
  start_ticks = MB.readName("CORE_TIMER") 
  op = ''

  -- do other stuff here, the timer is running
  LED_flash(2) -- show some status by the number of flashes. This is SLOW and variable. 

  if 1 then -- ready to read

    for sensor = 0, 1, 1 do -- get accumulated counts DAC0 and 1
      RNstr = string.format("DIO%.0f_EF_READ_A_AND_RESET", sensor) -- read and clear from here
      pulses = MB.readName(RNstr)                                  -- read and clear
      end_ticks = MB.readName("CORE_TIMER")
      
      local rollover = 0xFFFFFFFF
      local window
      if start_ticks <= end_ticks then
        window = end_ticks - start_ticks
      else    -- Clock rolled over
        window = rollover - start_ticks + end_ticks
      end

      local seconds = window / TicksPerSec
      local Hz = pulses / seconds
    
      MB.writeName(results_storage[sensor], Hz/Q) -- put results in user RAM for reading by the python script
      op = op .. (string.format("Sensor on DAC%1.0f %2.0f Hz %2.1f L/min  measured over %2.1f seconds         ", sensor, Hz, Hz/Q, seconds))
    end
    print (op)

  end -- 
end