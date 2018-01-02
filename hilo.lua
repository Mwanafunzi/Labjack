print("Get series of readings on logical input, calculate % that are low.\n writes result to user RAM 46000 \n T7 Serial No 470015741. Name My_T7_5741" )

local rw = {}  -- table holding FIO channels to read and destinTION ADDRESSES
rw[2000] = 46000  -- ie read FI02 and write value to USER_RAM0_F32 
rw[2001] = 46002
rw[2002] = 46004
rw[2003] = 46006

local hi = {}
local lo = {}
i = 0
interval = 10*1000  -- number of seconds to take readngs for
freq = 10   --milliseconds between readings

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
     prcnt = lo[r]/(hi[r]+lo[r])*100
     print(string.format("%2d, %4d:   %3d", i, r, prcnt))
     MB.W(w, 3, prcnt)    
  end
end

