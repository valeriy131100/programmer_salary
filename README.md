# progammer_salary
Программа для вычисления средней зарплаты московских программистов по языку программирования. Используются данные HeadHunter за последний месяц и данные Superjob. 

# Установка
Вам понадобится установленный Python 3.6-3.9 и git.

Склонируйте репозиторий:
```bash
$ git clone https://github.com/valeriy131100/progammer_salary
```

Создайте в этой папке виртуальное окружение:
```bash
$ python3 -m venv [полный путь до папки progammer_salary]
```

Активируйте виртуальное окружение и установите зависимости:
```bash
$ cd progammer_salary
$ source bin/activate
$ pip install -r requirements.txt
```
# Использование
Получите токен API Superjob. Это можно сделать [здесь](https://api.superjob.ru/).

Заполните файл .env.example и переименуйте его в .env или иным образом задайте переменную среды SUPERJOB_TOKEN.

Находясь в директории progammer_salary исполните:
```bash
$ bin/python main.py
```
Программа покажет среднюю зарплату программистов по данным SuperJob и HeadHunter в виде таблиц.
```text
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| TypeScript            | 1602             | 436                 | 207034           |
| Swift                 | 635              | 192                 | 241578           |
| Scala                 | 291              | 53                  | 238613           |
| Objective-C           | 236              | 62                  | 238693           |
| Go                    | 1046             | 240                 | 218915           |
| C                     | 3657             | 803                 | 173273           |
| C#                    | 1851             | 518                 | 186469           |
| C++                   | 1733             | 491                 | 175031           |
| PHP                   | 1881             | 877                 | 168272           |
| Ruby                  | 311              | 98                  | 211840           |
| Python                | 3324             | 565                 | 198262           |
| Java                  | 3634             | 547                 | 227560           |
| JavaScript            | 4490             | 910                 | 186079           |
+-----------------------+------------------+---------------------+------------------+
+SuperJob Moscow--------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| TypeScript            | 1                | 1                   | 360000           |
| Swift                 | 0                | 0                   | None             |
| Scala                 | 1                | 1                   | 240000           |
| Objective-C           | 0                | 0                   | None             |
| Go                    | 4                | 3                   | 220000           |
| C                     | 1                | 1                   | 240000           |
| C#                    | 18               | 13                  | 160807           |
| C++                   | 23               | 17                  | 164176           |
| PHP                   | 41               | 29                  | 151790           |
| Ruby                  | 4                | 4                   | 265075           |
| Python                | 15               | 10                  | 195350           |
| Java                  | 35               | 27                  | 243551           |
| JavaScript            | 8                | 6                   | 132750           |
+-----------------------+------------------+---------------------+------------------+
```

Программа может запускаться довольно долго, так как загрузка вакансий с HeadHunter занимает достаточно много времени.