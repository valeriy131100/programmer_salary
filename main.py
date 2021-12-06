from itertools import count

import requests
from datetime import datetime, timedelta
from environs import Env
from terminaltables import AsciiTable


def get_vacancies_from_hh(languages, from_date):
    vacancies_by_lang = dict()
    url = 'https://api.hh.ru/vacancies/'

    for language in languages:
        vacancies_items = []
        vacancies_found = 0

        for page in count():
            params = {
                'text': f'Программист {language}',
                'area': 1,  # код Москвы
                'date_from': from_date.isoformat(),
                'page': page
            }

            page_response = requests.get(url, params=params)
            page_response.raise_for_status()

            page_vacancies = page_response.json()

            vacancies_found = page_vacancies['found']
            page_vacancies_items = page_vacancies['items']
            vacancies_items.extend(page_vacancies_items)

            pages_number = page_response.json()['pages']

            if page == pages_number:
                break

        vacancies_salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies_items]
        processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

        vacancies_processed = len(processed_vacancies_salaries)
        if vacancies_processed:
            average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
        else:
            average_salary = None

        vacancies_by_lang[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary)
        }

    return vacancies_by_lang


def get_vacancies_from_sj(token, languages):
    vacancies_by_lang = dict()
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'X-Api-App-Id': token
    }

    for language in languages:
        vacancies_items = []
        vacancies_found = 0

        for page in count():
            params = {
                't': 4,  # код Москвы
                'catalogues': 48,  # Разработка, программирование
                'keywords[0][keys]': language,
                'keywords[0][srws]': 1,  # поиск только в должности
                'page': page
            }

            page_response = requests.get(url, params=params, headers=headers)
            page_response.raise_for_status()

            page_vacancies = page_response.json()

            vacancies_found = page_vacancies['total']
            page_vacancies_items = page_vacancies['objects']
            vacancies_items.extend(page_vacancies_items)

            if not page_vacancies['more']:
                break

        vacancies_salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_items]
        processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

        vacancies_processed = len(processed_vacancies_salaries)
        if vacancies_processed:
            average_salary = int(sum(processed_vacancies_salaries) / vacancies_processed)
        else:
            average_salary = None

        vacancies_by_lang[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }

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
    table_data = [
        [language, info['vacancies_found'], info['vacancies_processed'], info['average_salary']]
        for language, info in vacancies.items()
    ]

    table_data.insert(0, ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'])

    table_instance = AsciiTable(table_data, title)

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

    print_vacancies(get_vacancies_from_hh(languages, from_date), 'HeadHunter Moscow')
    print_vacancies(get_vacancies_from_sj(superjob_token, languages), 'SuperJob Moscow')
