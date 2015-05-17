import json

myJson = json.dumps({"logKey" : 10, "key": "myKey", "value" : "value"})

myJsonL = json.loads(myJson)

print myJsonL["key"]
