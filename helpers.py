from terminaltables import AsciiTable


def print_as_table(salaries, title):
    table_headers = [
        'Язык программирования',
        'Вакансий всего',
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
