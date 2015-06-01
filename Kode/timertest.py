from Heartbeat import Heartbeat
import time
hb = Heartbeat()

time.sleep(10)
if hb.state == "leader":
  print "changing state"
  hb.changeState()
  
  start_time = time.time() 
  
  while(hb.myIp == hb.leaderIp):
   print hb.leaderIp , hb.myIp
  end_time = time.time()
  print end_time - start_time
