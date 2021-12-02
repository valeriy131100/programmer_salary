import requests
from datetime import datetime, timedelta
from environs import Env
from terminaltables import AsciiTable

languages = [
    'TypeScript',
    'Swift',
    'Scala',
    'Objective-C',
    'Go',
    'C',
    'C#',
    'C++',
    'PHP',
    'Ruby',
    'Python',
    'Java',
    'JavaScript'
]

month_ago = datetime.today() - timedelta(days=30)


def get_vacancies_from_hh():
    vacancies_by_lang = dict()
    url = 'https://api.hh.ru/vacancies/'

    for language in languages:
        page = 0
        pages_number = 1
        vacancies_items = []
        vacancies_found = 0

        while page < pages_number:
            params = {
                'text': f'Программист {language}',
                'area': 1,  # код Москвы
                'date_from': month_ago.isoformat(),
                'page': page
            }

            page_response = requests.get(url, params=params)
            page_response.raise_for_status()

            page_vacancies = page_response.json()

            vacancies_found = page_vacancies['found']
            page_vacancies_items = page_vacancies['items']
            vacancies_items.extend(page_vacancies_items)

            pages_number = page_response.json()['pages']
            print(f'Processed {language} page {page} of {pages_number} pages')

            page += 1

        vacancies_salaries = list(map(lambda vacancy: predict_rub_salary_hh(vacancy), vacancies_items))
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


def get_vacancies_from_sj(token):
    vacancies_by_lang = dict()
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'X-Api-App-Id': token
    }

    for language in languages:
        vacancies_items = []
        vacancies_found = 0
        page = 0

        while True:
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

            page += 1

        vacancies_salaries = list(map(lambda vacancy: predict_rub_salary_sj(vacancy), vacancies_items))
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

    table_data.insert(0, ['Язык программирования', 'Ваканский найдено', 'Ваканский обработано', 'Средняя зарплата'])

    table_instance = AsciiTable(table_data, title)

    print(table_instance.table)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    superjob_token = env('SUPERJOB_TOKEN')

    print_vacancies(get_vacancies_from_hh(), 'HeadHunter Moscow')
    print_vacancies(get_vacancies_from_sj(superjob_token), 'SuperJob Moscow')
