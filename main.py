import requests
from helpers import print_as_table
from dotenv import load_dotenv
from os import getenv, environ
from statistics import mean


APP_NAME = 'DevmanJobParser/1.0'
HH_PROGRAMER_ID = 96
HH_MOSCOW_ID = 1
SUPERJOB_PROGRAMMING_ID = 48
SUPERJOB_MOSCOW_ID = 4
PERIOD = None
ACCEPTABLE_CURRENCY = ['rur', 'rub']
SEARCHING_PATTERNS_FOR_LANGUAGES = {
        'Python': 'Python',
        'Javascript': 'Javascript',
        'Java': 'Java NOT Javascript',
        'Kotlin': 'Kotlin',
        'Ruby': 'Ruby',
        'PHP': 'PHP',
        'C++': 'C++',
        'C#': 'C#',        
        'Go': 'Go'
}


def predict_rub_salary(salary_details: dict):
    if salary_details['currency'].lower() not in ACCEPTABLE_CURRENCY:
        return None

    salary_from = salary_details['salary_from']
    salary_to = salary_details['salary_to']

    if not salary_from:
        salary = salary_to * 1.2
    
    elif not salary_to:
        salary = salary_from * 0.8

    else:    
        salary = mean([salary_from, salary_to])
    
    return int(salary)


def get_predicted_salaries(salaries):
    predicted_salaries = []
    for salary in salaries:
        predicted_salary = predict_rub_salary(salary)
        if predicted_salary:
            predicted_salaries.append(predicted_salary)
    return predicted_salaries


def get_hh_page(searching_pattern, email, page, period, with_salary = True):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'professional_role': HH_PROGRAMER_ID,
        'area': HH_MOSCOW_ID,
        'period': period,
        'text': searching_pattern,
        'only_with_salary': with_salary,
        'page': page
    }
    headers = {'User-Agent': f'{APP_NAME} ({email})'}

    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()

    return response.json()


def get_salary_details_from_hh_vacancies(hh_vacancies):
    salaries = []
    for hh_vacancy in hh_vacancies['items']:
        salary = {
            'salary_from':hh_vacancy['salary']['from'],
            'salary_to':hh_vacancy['salary']['to'],
            'currency':hh_vacancy['salary']['currency']
        }
        salaries.append(salary)
    
    return salaries


def fetch_hh_average_salary(searching_pattern, email, period = PERIOD):
    pages = 1
    page = 0
    predicted_hh_salaries = []
    while page < pages:
        hh_vacancies = get_hh_page(searching_pattern, email, page, period)
        pages = hh_vacancies['pages']
        salaries = get_salary_details_from_hh_vacancies(hh_vacancies)
        predicted_hh_salaries.extend(get_predicted_salaries(salaries))
        page += 1 

    average_salary_stats = {
        'total': hh_vacancies['found'],
        'processed': len(predicted_hh_salaries),
        'average_salary': int(mean(predicted_hh_salaries))
    }

    return average_salary_stats


def fetch_salary_stats_for_hh_vacancies(searching_patterns, email):
    salary_stats_for_languages: dict = {}

    for lang, pattern in searching_patterns.items():
        print(f'Загружаются вакансии c hh.ru для {lang}')
        salary_stats = fetch_hh_average_salary(pattern, email)
        salary_stats_for_languages[lang] = salary_stats
       
    return salary_stats_for_languages


def get_salary_details_from_superjob_vacancies(superjob_vacancies):
    salaries = []
    for superjob_vacancy in superjob_vacancies['objects']:        
        salary = {
            'salary_from': superjob_vacancy['payment_from'],
            'salary_to': superjob_vacancy['payment_to'],
            'currency':superjob_vacancy['currency']
        }
        salaries.append(salary)
    
    return salaries


def get_superjob_page(token, keyword, page, per_page = 5, no_agreement = 1):
    url = 'https://api.superjob.ru/2.0/vacancies'

    headers = {
        'X-Api-App-Id': token
    }

    params = {
        'catalogues': SUPERJOB_PROGRAMMING_ID,
        'page': page,
        'count': per_page,
        'no_agreement': no_agreement,
        'keyword': keyword,
        'town': SUPERJOB_MOSCOW_ID
    }

    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()

    return response.json()


def fetch_superjob_average_salary(token, keyword):
    page = 0
    more = True
    predicted_salaries = []
    while more:
        vacancies = get_superjob_page(token, keyword, page)
        more = vacancies['more']
        salaries = get_salary_details_from_superjob_vacancies(vacancies)
        predicted_salaries.extend(get_predicted_salaries(salaries))
        if not predicted_salaries:
            average_salary = 0
        else:
            average_salary = int(mean(predicted_salaries))
        page += 1 

    average_salary_stats = {
        'total': vacancies['total'],
        'processed': len(predicted_salaries),
        'average_salary': average_salary
    }

    return average_salary_stats


def fetch_salary_stats_from_superjob_vacancies(token, languages):
    salary_stats_for_languages: dict = {}

    for lang in languages:
        print(f'Загружаются вакансии c superjob для {lang}')
        salary_stats = fetch_superjob_average_salary(token, lang)
        salary_stats_for_languages[lang] = salary_stats
       
    return salary_stats_for_languages


def main():
    load_dotenv()
    dev_email = getenv('DEV_EMAIL', 'example@email.com')
    superjob_token = environ['SUPERJOB_TOKEN']

    print('Начало загрузки вакансий с hh.ru')
    hh_salaries = fetch_salary_stats_for_hh_vacancies(
        SEARCHING_PATTERNS_FOR_LANGUAGES,
        dev_email
    )
    print(f'Сохранение вакансий hh.ru в файл')
    
    print('Начало загрузки вакансий с superjob.ru')
    sj_salaries = fetch_salary_stats_from_superjob_vacancies(
        superjob_token,
        SEARCHING_PATTERNS_FOR_LANGUAGES
    )
    print('Сохранение ваканский superjob.ru в файл')

    print_as_table(hh_salaries, 'hh.ru Moscow')
    print_as_table(sj_salaries, 'SuperJob.ru Moscow')


if __name__ == '__main__':
    main()
