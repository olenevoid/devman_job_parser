import json


def save_readable_json(dictionary, filename):
    json_string = json.dumps(dictionary, indent=4, ensure_ascii=False)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json_string)


def load_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        return json.loads(data)
