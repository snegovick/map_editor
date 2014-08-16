import state

import os
import json

class Project:

    def push_state(self, state):
        pass

    def serialize(self):
        return ""

    def deserialize(self, data):
        pass

    def load(self, path):
        f = open(path, "r")
        data = f.read()
        f.close()
        parsed_json = json.loads(data)
        state.state.deserialize(parsed_json)

    def save(self, path):
        if os.path.splitext(path)[1][1:].strip() != "map_project":
            path+=".map_project"

        f = open(path, "w")
        data = json.dumps(state.state.serialize())
        f.write(data)
        f.close()

project = Project()
