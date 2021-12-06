from itertools import count

import requests
from datetime import datetime, timedelta
from environs import Env
from terminaltables import AsciiTable


def get_language_vacancies_from_hh(language, from_date, area):
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

    vacancies_found = len(vacancies)
    vacancies_salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies]
    processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

    vacancies_processed = len(processed_vacancies_salaries)
    if vacancies_processed:
        average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
    else:
        average_salary = None

    return {
        'found': vacancies_found,
        'processed': vacancies_processed,
        'average_salary': int(average_salary)
    }


def get_language_vacancies_from_sj(token, language, area, catalogue, where_search):
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

    vacancies_found = len(vacancies)
    vacancies_salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies]
    processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

    vacancies_processed = len(processed_vacancies_salaries)
    if vacancies_processed:
        average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
    else:
        average_salary = None

    return {
        'found': vacancies_found,
        'processed': vacancies_processed,
        'average_salary': average_salary
    }


def get_vacancies_from_hh(languages, from_date, area):
    vacancies_by_lang = dict()

    for language in languages:
        vacancies_by_lang[language] = get_language_vacancies_from_hh(language, from_date, area)

    return vacancies_by_lang


def get_vacancies_from_sj(token, languages, area, catalogue, where_search):
    vacancies_by_lang = dict()

    for language in languages:
        vacancies_by_lang[language] = get_language_vacancies_from_sj(token, language, area, catalogue, where_search)

    return vacancies_by_lang


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return 1.2 * salary_from
    elif salary_to:
        return 0.8 * salary_to
    else:
        return None


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])
    else:
        return None


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if not salary:
        return None

    if salary['currency'] == 'RUR':
        return predict_salary(salary['from'], salary['to'])
    else:
        return None


def print_vacancies(vacancies, title):
    table = [
        [
            language,
            lang_vacancies['found'],
            lang_vacancies['processed'],
            lang_vacancies['average_salary']
        ]
        for language, lang_vacancies in vacancies.items()
    ]

    table.insert(0, ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'])

    table_instance = AsciiTable(table, title)

    print(table_instance.table)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    superjob_token = env('SUPERJOB_TOKEN')
    languages = env.list('LANGUAGES',
                         default=['TypeScript', 'Swift', 'Scala', 'Objective-C', 'Go',
                                  'C', 'C#', 'C++', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript'])
    days_ago = env.int('DAYS_AGO', default=30)
    from_date = datetime.today() - timedelta(days=days_ago)

    HH_MOSCOW = 1

    SEARCH_ONLY_NAME = 1
    DEVELOPMENT = 48
    SJ_MOSCOW = 4

    hh_vacancies = get_vacancies_from_hh(languages, from_date, area=HH_MOSCOW)
    sj_vacancies = get_vacancies_from_sj(superjob_token, languages,
                                         area=SJ_MOSCOW, catalogue=DEVELOPMENT, where_search=SEARCH_ONLY_NAME)

    print_vacancies(hh_vacancies, 'HeadHunter Moscow')
    print_vacancies(sj_vacancies, 'SuperJob Moscow')
