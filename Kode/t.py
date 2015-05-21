from Heartbeat import Heartbeat

hb = Heartbeat()

while(1):
  if hb.getState() == "follower":
    if hb.get("123") == None:
       hb.set("123", "456")
  elif hb.getState() == "leader":
    val = hb.get("123")
    if not (val == None):
      print hb.get("123")
