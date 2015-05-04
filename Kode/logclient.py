from socket import *
import Log


sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind( ("", 5005))
sock.setblocking(0)
ipLog = Log.log()

while(1):
  try:
    myInput, addr = sock.recvfrom(1024)
  
    ipLog.parse(myInput)
    print ipLog.getLog()
  except:
    pass



