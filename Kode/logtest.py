from socket import *
import Log


sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind( ("", 5005))
sock.setblocking(0)
ipLog = Log.log()

while(1):
  myInput = raw_input()
  
  if myInput[0:3] == "ad:":
    sock.sendto(myInput, ("192.168.43.69", 5005))
    ipLog.add(myInput[3:])
  if myInput[0:3] == "re:":
    sock.sendto(myInput, ("192.168.43.69", 5005))
    ipLog.remove(myInput[3:])
  if myInput[0:3] == "ow:":
     sock.sendto("ow:"+str(ipLog.getLog()) + "-" + str(ipLog.getList()), ("192.168.43.69", 5005))
  if myInput[0:3] == "co:":
     sock.sendto(myInput, ("192.168.43.69", 5005))
     print "waaat"
     ipLog.commit(myInput[3:])

  print ipLog.getLog()
  print ipLog.getList()


