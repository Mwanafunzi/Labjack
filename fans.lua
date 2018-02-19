print("Sampling O2 on AIN4 and turning fan on or off via DAC1")

-- watches for low O2 or vent open and activates additinal fans in the biorepository
-- there are 2 fans, separately controlled by DAC0 and DAC1 
-- also puts averaged values for O2 levels onto user memory. so can be read by external script. Avoids ned for EF on AIN4 which reduces RAM usage on the T7

--------------------------------------------------------------
local minO2 = 20.7    -- TURN on fans if O2 below this level
local scanRate = 500  --Rate that data will be read in Hz
local numScans = 50  --number of scans of O2 level to collect

local mbWrite=MB.W        --create local functions for reading/writing at faster speeds
local mbRead=MB.R

local vent_addr = 2006   --address for vent solenoid. If active a fill is imminent
local O2_addr = 8

local fan_0_addr = 1000
local fan_1_addr = 1002

local O2Avoutput = 46000 -- USER_RAM0_F32. 

persistence = 4*60    -- number of seconds to persist fans after return to normal O2 or vent
local sleep = 3 -- seconds pause between loops

LJ.IntervalConfig(0, 1000/scanRate)   --Define the scan interval in ms.
local checkInterval=LJ.CheckInterval  --create local function to check the interval for faster loop time

mbWrite(fan_0_addr, 3, 4.5)       --Set DAC0 to 4.5V turns it off, type is 3
mbWrite(fan_1_addr, 3, 4.5)       --Set DAC1 to 4.5V turns it off, type is 3


while 1 do  --FOREVER
  
local avgData=0
local iter=0

-- average the O2 signal for better accuracy 

while iter<numScans do          --loop as fast as possible until number of scans has been aquired
  if checkInterval(0) then      --if interval time has been reached, add 1 to iter and take data reading
    iter=1+iter
    local data0 = mbRead(O2_addr,3)      --take a reading on the AIN4 line
    avgData=data0+avgData                --add data to previous data readings 
  end
end

local avg=(10*(avgData/numScans))            --divide added data by the number of scans to get average and multiply by 10 to get to O2 %


mbWrite(O2Avoutput, 3, avg)   -- write the av O2 to USER_RAM0_F32, so can be accessed by external prog

local fanoff = ((mbRead(fan_0_addr,3) > 3.5)  or  (mbRead(fan_1_addr,3) > 3.5)) --is either fan on?. Look at DAC0 and DAC1
local lowO2 = avg < minO2
local venton = mbRead(vent_addr,3) >0.8

print("vent on: ",venton, "      lowO2: ",lowO2, avg)

if ((lowO2) or (venton)) then
  if fanoff then
    print ("LOW O2 and fan is off, turning on fan boost")

    mbWrite(fan_0_addr, 3, 0)       -- Set DAC0 to 0V turns it on   
    mbWrite(fan_1_addr, 3, 0)       -- Set DAC1 to 0v turns it on

  else
    print ("fan already on, nothing to do")
  end
  
  LJ.IntervalConfig(1, 1000)      -- START A TIMER base tick of 1 second
  tick = 0                        -- zero the timer
  
elseif not fanoff then
    print ("all ok, but fan on, turn it off ")
    if (checkInterval(1) ) then 
         tick = tick + 1
         if tick > persistence then
           mbWrite(fan_0_addr, 3, 4.5)       --Set DAC to 4.5V turns it off, type is 3
           mbWrite(fan_1_addr, 3, 4.5)       --Set DAC to 4.5V turns it off, type is 3
         else
                 print ("All ok, waiting for timer to expire before cancelling fan boost ", tick," of ",persistence," seconds")
         end
    else
   end
end 
  
  
--- pause ---
LJ.IntervalConfig(2, 1000)      -- START Another TIMER with a base tick of 1 second
local p = 0
while p < sleep do
 if (checkInterval(2) ) then 
   p = p+1
  -- print (p)
 end
end
   




end