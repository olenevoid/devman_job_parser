import json
from terminaltables import AsciiTable


def save_readable_json(dictionary, filename):
    json_string = json.dumps(dictionary, indent=4, ensure_ascii=False)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json_string)


def load_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read()
        return json.loads(data)


def print_as_table(salaries, title):
    table_headers = [
        'Язык программирования',
        'Вакансий с зарплатой',
        'Вакансий обработано',
        'Средняя зарплата'
    ]
    
    table_data = [
        table_headers,
    ]

    for lang, salary in salaries.items():
        row = [
            lang,
            salary['total'],
            salary['processed'],
            salary['average_salary']
        ]

        table_data.append(row)
    
    table = AsciiTable(table_data, title)
    
    print(table.table)
