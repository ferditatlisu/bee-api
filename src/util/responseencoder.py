from json import JSONEncoder
import json

class ResponseEncoder(JSONEncoder):
    def default(self, o):
        if type(o) is bytes:
            return o.decode('utf-8')
        else:
            return json.JSONEncoder.encode(self, o)