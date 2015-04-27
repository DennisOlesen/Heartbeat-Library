

class log():

  def __init__(self):
   self.log = []
   self.ipList = []  
  def add(self, ip):
    self.log.append([self.getKey()+1, "ad:"+ str(ip)])
    if ip not in self.ipList:
      self.ipList.append(ip)
    
    return 1

  def remove(self, ip):
    self.ipList.remove(ip)
    self.log.append([self.getKey()+1, "re:" + str(ip)])

  def overwrite(self, newLog):
    data = newLog.split(",") 
    self.log = eval(data[0])
    self.ipList = eval(data[1])

  def commit(self, key):
    for sub in self.log:
       if sub[0] <= key:
         self.log.remove(sub)
    pass

  def parse(self, text):
    textSplit = text.split()    
    for sub in textSplit:
      if sub[0:3] == "ad:":
        self.add(sub[3:])
      if sub[0:3] == "re:":
        self.remove(sub[3:])
      if sub[0:3] == "co:":
        self.commit(int(sub[3:]))
      if sub[0:3] == "ow:":
        self.overwrite(sub[3:])

  def getKey(self):
    if self.log == []:
      return -1
    return self.log[len(self.log)-1][0]
  
  def getList(self):
    return self.ipList

  def getLog(self):
    return self.log

  def compile(self,key):
    text = ""
    for sub in self.log:
      if sub[0] > key:
        text = text + sub[1] + " "
    return text
