import requests
import json
from dotenv import load_dotenv
from os import getenv
from statistics import mean


APP_NAME = 'DevmanJobParser/1.0'
HH_PROGRAMER_ID = 96
HH_MOSCOW_ID = 1
PERIOD = None
LANG_REQUEST = {
        'Python': 'Python',
        'Javascript': 'Javascript',
        'Java': 'Java NOT Javascript',
        'Ruby': 'Ruby',
        'PHP': 'PHP',
        'C++': 'C++',
        'C#': 'C#',
        'C': 'C NOT C# NOT C++',
        'Go': 'Go'
}

LANG_REQUEST_SHORT = {
        'Python': 'Python',
        'Javascript': 'Javascript',
        'Java': 'Java NOT Javascript'
}


def predict_rub_salary(job: dict):
    if job['salary']['currency'] != 'RUR':
        return None

    salary_from = job['salary']['from']
    salary_to = job['salary']['to']

    if not salary_from:
        salary = int(salary_to) * 1.2
    
    elif not salary_to:
        salary = int(salary_from) * 0.8

    else:    
        salary = mean([int(salary_from), int(salary_to)])
    
    return int(salary)


def get_salaries(jobs):
    salaries = []
    for job in jobs:
        salary = predict_rub_salary(job)
        if salary:
            salaries.append(salary)
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


def get_hh_job_salaries(request_text, email, period = PERIOD):
    pages = 1
    page = 0
    salaries = []
    while(page < pages):
        raw_jobs = get_hh_page(request_text, email, page, period)
        pages = raw_jobs['pages']        
        page_salaries = get_salaries(raw_jobs['items'])
        salaries = [*salaries, *page_salaries]
        page += 1 

    job_salaries = {
        'total': raw_jobs['found'],
        'processed': len(salaries),
        'average_salary': int(mean(salaries))
    }

    return job_salaries


def get_popular_hh_jobs(lang_request, email):
    popular_langs: dict = {}

    for lang, request in lang_request.items():
        print(f'Загружаются вакансии для {lang}')
        jobs = get_hh_job_salaries(request, email)
        popular_langs[lang] = jobs
       
    return popular_langs


def save_readable_json(dictionary, filename):
    json_string = json.dumps(dictionary, indent=4, ensure_ascii=False)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(json_string)


def test_hh_jobs(email):
    hh_jobs = get_hh_job_salaries(LANG_REQUEST['Python'], email)    
    save_readable_json(hh_jobs, 'hh_jobs_salary.json')    


def test_popular_hh_jobs(email):
    pop_jobs = get_popular_hh_jobs(LANG_REQUEST, email)
    save_readable_json(pop_jobs, 'pop_jobs.json')


def main():
    load_dotenv()
    dev_email = getenv('DEV_EMAIL', 'example@email.com')
    test_popular_hh_jobs(dev_email)
    


if __name__ == '__main__':
    main()
