import requests
from datetime import datetime, timedelta

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


def predict_rub_salary(vacancy):
    salary = vacancy['salary']
    if not salary:
        return None

    currency = salary['currency']
    salary_from = salary['from']
    salary_to = salary['to']
    if currency != 'RUR':
        return None
    elif salary_from and salary_to:
        return (salary_from+salary_to) / 2
    elif salary_from:
        return 1.2 * salary_from
    elif salary_to:
        return 0.8 * salary_to
    else:
        return None


if __name__ == '__main__':
    vacancies_by_lang = dict()

    for language in languages:
        url = 'https://api.hh.ru/vacancies/'
        params = {
            'text': f'Программист {language}',
            'area': 1,  # код Москвы
            'date_from': month_ago.isoformat()
        }

        response = requests.get(url, params=params)
        vacancies = response.json()
        vacancies_found = vacancies['found']

        vacancies_items = vacancies['items']
        vacancies_salaries = list(map(lambda vacancy: predict_rub_salary(vacancy), vacancies_items))
        processed_vacancies_salaries = [salary for salary in vacancies_salaries if salary]

        vacancies_processed = len(processed_vacancies_salaries)
        average_salary = sum(processed_vacancies_salaries) / vacancies_processed

        vacancies_by_lang[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary)
        }

    print(vacancies_by_lang)
