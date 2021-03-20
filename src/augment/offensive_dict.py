import json


class OffensiveDict:
    def __init__(self, path):
        with open(path) as f:
            self.offensive_dict = json.load(f)

if __name__=="__main__":
    d = OffensiveDict("../../polish_offensive_dict.json")
    print(d.offensive_dict)