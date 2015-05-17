import json

myJson = json.dumps({"logKey" : 10, "key": "myKey", "value" : "value"}, separators=(',',':'))

myJsonL = json.loads(myJson)

print myJson
