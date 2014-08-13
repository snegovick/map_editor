import state

import json

class Project:

    def push_state(self, state):
        pass

    def serialize(self):
        return json.dumps({"type": "tileset", "format_version": 1, "state": state.state.serialize()})

    def deserialize(self, data):
        parsed_json = json.loads(data)
        if parsed_json["format_version"] == 1 and parsed_json["type"] == "tileset":
            state.state.deserialize(parsed_json["state"])

    def load(self, path):
        f = open(path, "r")
        data = f.read()
        f.close()
        self.deserialize(data)
            

    def save(self, path):
        f = open(path, "w")
        f.write(self.serialize())
        f.close()

project = Project()
