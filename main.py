import json

def load_json(fileName):
           data = {}
           with open(fileName, 'r') as f:
                     data = json.load(f)
           return data

ooni_data = load_json("datasets/1.json")