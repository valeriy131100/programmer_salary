from itertools import count

import requests
from datetime import datetime, timedelta
from environs import Env
from terminaltables import AsciiTable


def get_lang_vacancies_stat_from_hh(language, from_date, area):
    url = 'https://api.hh.ru/vacancies/'
    vacancies = []

    for page in count():
        params = {
            'text': f'Программист {language}',
            'area': area,
            'date_from': from_date.isoformat(),
            'page': page
        }

        page_response = requests.get(url, params=params)
        page_response.raise_for_status()

        page_vacancies = page_response.json()

        vacancies.extend(page_vacancies['items'])

        pages_number = page_vacancies['pages']

        if page == pages_number - 1:
            break

    vacancies_found = page_vacancies['found']
    vacancies_salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies]
    processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

    vacancies_processed = len(processed_vacancies_salaries)
    if vacancies_processed:
        average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
    else:
        average_salary = None

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': int(average_salary)
    }


def get_lang_vacancies_stat_from_sj(token, language, area, catalogue, where_search):
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'X-Api-App-Id': token
    }
    vacancies = []

    for page in count():
        params = {
            't': area,
            'catalogues': catalogue,
            'keywords[0][keys]': language,
            'keywords[0][srws]': where_search,
            'page': page
        }

        page_response = requests.get(url, params=params, headers=headers)
        page_response.raise_for_status()

        page_vacancies = page_response.json()

        vacancies.extend(page_vacancies['objects'])

        if not page_vacancies['more']:
            break

    vacancies_found = page_vacancies['total']
    vacancies_salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies]
    processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

    vacancies_processed = len(processed_vacancies_salaries)
    if vacancies_processed:
        average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
    else:
        average_salary = None

    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary
    }


def get_vacancies_stat_from_hh(languages, from_date, area):
    vacancies_stat = dict()

    for language in languages:
        vacancies_stat[language] = get_lang_vacancies_stat_from_hh(language, from_date, area)

    return vacancies_stat


def get_vacancies_stat_from_sj(token, languages, area, catalogue, where_search):
    vacancies_stat = dict()

    for language in languages:
        vacancies_stat[language] = get_lang_vacancies_stat_from_sj(token, language, area, catalogue, where_search)

    return vacancies_stat


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return 1.2 * salary_from
    elif salary_to:
        return 0.8 * salary_to


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']

    if salary and salary['currency'] == 'RUR':
        return predict_salary(salary['from'], salary['to'])


def get_vacancies_stat_table(vacancies, title):
    table = [
        [
            language,
            stat['vacancies_found'],
            stat['vacancies_processed'],
            stat['average_salary']
        ]
        for language, stat in vacancies.items()
    ]

    table.insert(0, ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'])

    return AsciiTable(table, title).table


if __name__ == '__main__':
    env = Env()
    env.read_env()
    superjob_token = env('SUPERJOB_TOKEN')
    languages = env.list('LANGUAGES',
                         default=['TypeScript', 'Swift', 'Scala', 'Objective-C', 'Go',
                                  'C', 'C#', 'C++', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript'])
    days_ago = env.int('DAYS_AGO', default=30)
    from_date = datetime.today() - timedelta(days=days_ago)

    hh_moscow = 1

    search_only_name = 1
    development = 48
    sj_moscow = 4

    hh_vacancies_stat = get_vacancies_stat_from_hh(languages, from_date, area=hh_moscow)
    hh_table = get_vacancies_stat_table(hh_vacancies_stat, 'HeadHunter Moscow')
    print(hh_table)

    sj_vacancies_stat = get_vacancies_stat_from_sj(superjob_token, languages,
                                                   area=sj_moscow, catalogue=development, where_search=search_only_name)
    sj_table = get_vacancies_stat_table(sj_vacancies_stat, 'SuperJob Moscow')
    print(sj_table)
