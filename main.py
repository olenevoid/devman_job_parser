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
LANG_REQUEST = {
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


def predict_rub_salary(job: dict):
    if job['currency'].lower() not in ACCEPTABLE_CURRENCY:
        return None

    salary_from = job['salary_from']
    salary_to = job['salary_to']

    if not salary_from:
        salary = salary_to * 1.2
    
    elif not salary_to:
        salary = salary_from * 0.8

    else:    
        salary = mean([salary_from, salary_to])
    
    return int(salary)


def get_salaries(jobs):
    salaries = []
    for job in jobs:
        predicted_salary = predict_rub_salary(job)
        if predicted_salary:
            salaries.append(predicted_salary)
    return salaries


def get_hh_page(request_text, email, page, period):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'professional_role': HH_PROGRAMER_ID,
        'area': HH_MOSCOW_ID,
        'period': period,
        'text': request_text,
        'only_with_salary': True,
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


def fetch_hh_salaries(request_text, email, period = PERIOD):
    pages = 1
    page = 0
    salaries = []
    while(page < pages):
        hh_vacancies = get_hh_page(request_text, email, page, period)
        pages = hh_vacancies['pages']
        jobs = get_salary_details_from_hh_vacancies(hh_vacancies)
        page_salaries = get_salaries(jobs)
        salaries.extend(page_salaries)
        page += 1 

    average_salaries = {
        'total': hh_vacancies['found'],
        'processed': len(salaries),
        'average_salary': int(mean(salaries))
    }

    return average_salaries


def fetch_salary_stats_for_hh_vacancies(lang_request, email):
    popular_langs: dict = {}

    for lang, request in lang_request.items():
        print(f'Загружаются вакансии c hh.ru для {lang}')
        jobs = fetch_hh_salaries(request, email)
        popular_langs[lang] = jobs
       
    return popular_langs


def convert_superjob_raw_jobs_to_jobs(raw_superjob_jobs):
    jobs = []
    for raw_superjob_job in raw_superjob_jobs['objects']:
        salary_from = raw_superjob_job['payment_from']
        salary_to = raw_superjob_job['payment_to']
        job = {
            'salary_from': salary_from,
            'salary_to': salary_to,
            'currency':raw_superjob_job['currency']
        }
        jobs.append(job)
    
    return jobs

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


def fetch_superjob_salaries(token, keyword):
    page = 0
    more = True
    salaries = []
    while(more):
        superjob_salaries = get_superjob_page(token, keyword, page)
        more = superjob_salaries['more']
        jobs = convert_superjob_raw_jobs_to_jobs(superjob_salaries)
        page_salaries = get_salaries(jobs)
        salaries.extend(page_salaries)
        if not salaries:
            average_salary = 0
        else:
            average_salary = int(mean(salaries))
        page += 1 

    average_salaries = {
        'total': superjob_salaries['total'],
        'processed': len(salaries),
        'average_salary': average_salary
    }

    return average_salaries


def fetch_salary_stats_from_superjob_vacancies(token, lang_request):
    popular_langs: dict = {}

    for lang in lang_request:
        print(f'Загружаются вакансии c superjob для {lang}')
        jobs = fetch_superjob_salaries(token, lang)
        popular_langs[lang] = jobs
       
    return popular_langs


def main():
    load_dotenv()
    dev_email = getenv('DEV_EMAIL', 'example@email.com')
    superjob_token = environ['SUPERJOB_TOKEN']

    print('Начало загрузки вакансий с hh.ru')
    hh_salaries = fetch_salary_stats_for_hh_vacancies(LANG_REQUEST, dev_email)
    print(f'Сохранение вакансий hh.ru в файл')
    
    print('Начало загрузки вакансий с superjob.ru')
    sj_salaries = fetch_salary_stats_from_superjob_vacancies(superjob_token, LANG_REQUEST)
    print('Сохранение ваканский superjob.ru в файл')

    print_as_table(hh_salaries, 'hh.ru Moscow')
    print_as_table(sj_salaries, 'SuperJob.ru Moscow')


if __name__ == '__main__':
    main()
