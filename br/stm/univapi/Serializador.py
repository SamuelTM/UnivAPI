import json


class Serializador(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
