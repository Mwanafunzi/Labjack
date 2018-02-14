print("Get series of readings on logical input, calculate % that are low.\n writes result to user RAM 46000 \n T7 Serial No 470015741. Name My_T7_5741" )


function table.sum(arr, length) 
      --same as if <> then <> else <>
      return length == 1 and arr[1] or arr[length] + table.sum(arr, length -1)
end
 

--new version
-- saves a moving window average to smooth out readings

local interval = 30*1000  -- number of seconds to take readngs for
local freq = 10   --milliseconds between readings
local list_size = 10 --maximum size of moving window, ie number of readings held in list

local rslts = {} -- will be a 2 dimensional list, a list for each channel


local rw = {}  -- table holding FIO channels to read and destinTION ADDRESSES
rw[2000] = 46000  -- ie read FI02 and write value to USER_RAM0_F32 
rw[2001] = 46002
rw[2002] = 46004
rw[2003] = 46006

local hi = {}
local lo = {}

for r, w in pairs(rw) do  -- initialise lists for results for each channel
  rslts[r] = {}
end


i = 0



while true do
  for r, w in pairs(rw) do
    hi[r] = 0  -- matching counters
    lo[r] = 0
  end
  print('--------------')
  

  LJ.IntervalConfig(0, interval)           --set interval on counter 0
  LJ.IntervalConfig(1, 1)           --set interval on counter 1
  while  not LJ.CheckInterval(0)  do
      if LJ.CheckInterval(1)   then
       for r, w in pairs(rw) do
         if MB.R(r, 0) == 0 then  --read address 2002 (FIO2), type is 0
          lo[r]=lo[r]+1
        else 
          hi[r] = hi[r] + 1
        end
       end
       LJ.IntervalConfig(1, freq)           --set interval on counter 0
        
        
        
        
      end
  end
  i = i +1
   
  for r, w in pairs(rw) do
     ratio = lo[r]/(hi[r]+lo[r]) * 10000 * 8.48
     --print(string.format("%2d, %4d:   %3d", i, r, ratio))
     -- Now add this to running list
     table.insert(rslts[r], 1, ratio) -- add new result at start of the list
     if table.getn(rslts[r]) > list_size then
         table.remove(rslts[r]) -- remove the last if its full
     end  
     --print ( i, ratio, ': ', rslts[r][1],rslts[r][2],rslts[r][3],rslts[r][4],rslts[r][5],rslts[r][6] )
     --print(i, table.sum(rslts[r],#rslts[r])/#rslts[r])
     local av = table.sum(rslts[r],#rslts[r])/#rslts[r]
     print(string.format("%2d - %4d:   %3d", i, r, av))

     MB.W(w, 3, av)   -- write the array average to the labjack
  end
end

