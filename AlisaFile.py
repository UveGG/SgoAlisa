from flask import request
import logging
import json
from requests_sorting import lessons, skills, logout, reconnect
from models import Region, City, School, User
import requests


def init_route(app, db):
    logging.basicConfig(level=logging.INFO)
    sessionStorage = {}

    @app.route('/post', methods=['POST'])
    def main():
        db.create_all()
        logging.info('Request: %r', request.json)
        response = {
            'session': request.json['session'],
            'version': request.json['version'],
            'response': {
                'end_session': False
            }
        }

        handle_dialog(request.json, response)

        logging.info('Response: %r', response)

        return json.dumps(response)

    def handle_dialog(req, res):
        user_id = req['session']['user_id']
        user_answer = req['request']['original_utterance'].lower()

        if req['session']['new']:

            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': False
                },
                {
                    'title': 'На этом все',
                    'hide': False
                }
            ]

            alisa_answer = 'Привет! Это моё умение предназначено для помощи школьнику и его родителям. ' \
                           'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                           ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                           ' четвертей. Всю эту информацию я беру с сайта "Сетевой город. Образование"' \
                           ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                           ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                           ' попросите меня выйти из Вашего аккаунта. Если Вы хотите завершить работу со мной - ' \
                           'скажите волшебную фразу: "на этом все". Чтобы перечитать мои возможности напишите' \
                           ' "помощь" или "Что ты можешь?".'

            if not User.query.filter_by(user_id=user_id).first():
                sessionStorage[user_id] = {}
                sessionStorage[user_id]['region'] = None
                sessionStorage[user_id]['city'] = None
                sessionStorage[user_id]['school'] = None
                sessionStorage[user_id]['login'] = None
                sessionStorage[user_id]['password'] = None
                sessionStorage[user_id]['authorisation'] = True
                sessionStorage[user_id]['connection'] = [False, 'new_account', 'waiting']

                alisa_answer += 'Но сначала нужно авторизироваться, чтобы мне было с чем работать. ' \
                                'Для авторизации мне нужен номер Вашего региона, населённый пункт, школа, ' \
                                'а также Ваш логин и пароль. Сейчас я прошу Вас написать номер региона (отдельным сообщением).'
            else:
                user = User.query.filter_by(user_id=user_id).first()

                sessionStorage[user_id] = {}
                sessionStorage[user_id]['region'] = user.region_id
                sessionStorage[user_id]['city'] = user.city_id
                sessionStorage[user_id]['school'] = user.school_id
                sessionStorage[user_id]['login'] = user.login
                sessionStorage[user_id]['password'] = user.password
                sessionStorage[user_id]['connection'] = [False, 'old_account', 'waiting']
                sessionStorage[user_id]['authorisation'] = False

                alisa_answer += ' А сейчас я обновляю базу данных. Подождите чуть-чуть, пожалуйста!'

                User.delete(User.query.filter_by(user_id=user_id).first())
                reload(user_id, [])  # Обновление базы данных

            res['response']['text'] = alisa_answer
            return

        if 'на этом вс' in user_answer:  # Завершение работы с умением
            res['response']['end_session'] = True
            alisa_answer = 'Спасибо, что использовали "Сетевой город" в Яндекс.Алисе! До новых встреч!'
            res['response']['text'] = alisa_answer
            return

        # noinspection PySimplifyBooleanCheck
        if sessionStorage[user_id]['authorisation']:

            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': False
                },
                {
                    'title': 'Что ты можешь?',
                    'hide': False
                },
                {
                    'title': 'Отмена',
                    'hide': False
                }
            ]

            if 'отмена' in user_answer:
                res['response']['buttons'] = [
                    {
                        'title': 'Помощь',
                        'hide': False
                    },
                    {
                        'title': 'Что ты можешь?',
                        'hide': False
                    },
                    {
                        'title': 'На этом все',
                        'hide': False
                    }
                ]

                alisa_answer = 'Хорошо, давайте начнем вход в аккаунт заново. Если вы хотите покинуть умение напишите "На этом все".'
                res['response']['text'] = alisa_answer

                sessionStorage[user_id]['region'] = None
                sessionStorage[user_id]['city'] = None
                sessionStorage[user_id]['school'] = None
                sessionStorage[user_id]['login'] = None
                sessionStorage[user_id]['password'] = None

                return

            if sessionStorage[user_id]['region'] is None:
                if 'помощь' in user_answer or 'помоги' in user_answer:
                    alisa_answer = 'Напишите номер Вашего региона для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer

                    res['response']['buttons'] = [
                        {
                            'title': 'Помощь',
                            'hide': False
                        },
                        {
                            'title': 'Что ты можешь?',
                            'hide': False
                        },
                        {
                            'title': 'На этом все',
                            'hide': False
                        }
                    ]

                    return
                if 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                   ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                   ' четвертей.' \
                                   ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                   ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                   ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                   ' "Помощь" или "Что ты можешь?". Чтобы завершить работу с "Сетевым городом" напишите "на этом все".' \
                                   ' А сейчас напишите номер Вашего субъекта РФ.'
                    res['response']['text'] = alisa_answer
                    return
                if user_answer == '84':
                    sessionStorage[user_id]['region'] = user_answer
                    Region.add(regionid=user_answer)
                    City.add(cityid=user_answer, name='muhosransk', region_id=user_answer)
                    School.add(schoolid=user_answer, name='gubernskaya', city_id=user_answer)

                if not Region.query.filter_by(regionid=user_answer).first():
                    alisa_answer = 'Вы уверены, что такой регион существует? Я о нем не слышала!'
                    res['response']['text'] = alisa_answer
                    return
                else:
                    sessionStorage[user_id]['region'] = user_answer
                    alisa_answer = 'Отлично! Теперь выберите название Вашего населённого пункта!'  # Достать названия всех
                    res['response']['text'] = alisa_answer

                    cities = City.query.filter_by(region_id=sessionStorage[user_id]['region'])
                    for city in cities:
                        res['response']['buttons'].append({
                            'title': city.name,
                            'hide': False
                        })

                    return

            if sessionStorage[user_id]['city'] is None:
                if 'помощь' in user_answer or 'помоги' in user_answer:
                    alisa_answer = 'Выберите Ваш населенный пункт для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer

                    cities = City.query.filter_by(region_id=sessionStorage[user_id]['region'])
                    for city in cities:
                        res['response']['buttons'].append({
                            'title': city.name,
                            'hide': False
                        })

                    return

                if 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                   ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                   ' четвертей.' \
                                   ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                   ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                   ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                   ' "Помощь" или "Что ты можешь?". Чтобы завершить работу с "Сетевым городом" напишите "на этом все".' \
                                   ' А сейчас выберите Ваш населенный пункт.'
                    res['response']['text'] = alisa_answer

                    cities = City.query.filter_by(region_id=sessionStorage[user_id]['region'])
                    for city in cities:
                        res['response']['buttons'].append({
                            'title': city.name,
                            'hide': False
                        })

                    return

                if not City.query.filter_by(region_id=sessionStorage[user_id]['region'], name=user_answer).first():
                    alisa_answer = 'Что это за место? Я о нем не слышала!'
                    res['response']['text'] = alisa_answer

                    cities = City.query.filter_by(region_id=sessionStorage[user_id]['region'])
                    for city in cities:
                        res['response']['buttons'].append({
                            'title': city.name,
                            'hide': False
                        })
                    return
                else:
                    sessionStorage[user_id]['city'] = City.query.filter_by(region_id=sessionStorage[user_id]['region'],
                                                                           name=user_answer).first().cityid
                    alisa_answer = 'Отлично! Теперь выберите название Вашей образовательной организации!'  # Достать названия всех
                    res['response']['text'] = alisa_answer

                    schools = School.query.filter_by(city_id=sessionStorage[user_id]['city'])
                    for school in schools:
                        res['response']['buttons'].append({
                            'title': school.name,
                            'hide': False
                        })

                    return

            if sessionStorage[user_id]['school'] is None:
                if 'помощь' in user_answer or 'помоги' in user_answer:
                    alisa_answer = 'Выберите Вашу образовательную организацию для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer

                    schools = School.query.filter_by(city_id=sessionStorage[user_id]['city'])
                    for school in schools:
                        res['response']['buttons'].append({
                            'title': school.name,
                            'hide': False
                        })

                    return
                if 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                   ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                   ' четвертей.' \
                                   ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                   ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                   ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                   ' "Помощь" или "Что ты можешь?". Чтобы завершить работу с "Сетевым городом" напишите "на этом все".' \
                                   ' А сейчас выберите Вашу образовательную организацию.'
                    res['response']['text'] = alisa_answer

                    schools = School.query.filter_by(city_id=sessionStorage[user_id]['city'])
                    for school in schools:
                        res['response']['buttons'].append({
                            'title': school.name,
                            'hide': False
                        })

                    return

                if not School.query.filter_by(city_id=sessionStorage[user_id]['city'], name=user_answer).first():
                    alisa_answer = 'Что это за место? Я о нем не слышала!'
                    res['response']['text'] = alisa_answer

                    schools = School.query.filter_by(city_id=sessionStorage[user_id]['city'])
                    for school in schools:
                        res['response']['buttons'].append({
                            'title': school.name,
                            'hide': False
                        })
                    return
                else:
                    sessionStorage[user_id]['school'] = School.query.filter_by(city_id=sessionStorage[user_id]['city'],
                                                                               name=user_answer).first().schoolid
                    alisa_answer = 'Отлично! Теперь скажите мне Ваш логин от аккаунта в "Сетевом городе"!'  # Достать названия всех
                    res['response']['text'] = alisa_answer
                    return

            if sessionStorage[user_id]['login'] is None:
                if 'помощь' in user_answer or 'помоги' in user_answer:
                    alisa_answer = 'Напишите Ваш логин для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer

                    return

                if 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                   ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                   ' четвертей.' \
                                   ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                   ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                   ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                   ' "Помощь" или "Что ты можешь?". Чтобы завершить работу с "Сетевым городом" напишите "на этом все".' \
                                   ' А сейчас напишите логин от Вашего аккаунта в "Сетевом городе".'

                    res['response']['text'] = alisa_answer

                    return

                sessionStorage[user_id]['login'] = user_answer

                alisa_answer = 'Отлично! А теперь скажите Ваш пароль для входа в "Сетевой город".'
                res['response']['text'] = alisa_answer

                return

            if sessionStorage[user_id]['password'] is None:
                if 'помощь' in user_answer or 'помоги' in user_answer:
                    alisa_answer = 'Напишите Ваш пароль для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer
                    return

                if 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                   ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                   ' четвертей.' \
                                   ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                   ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                   ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                   ' "Помощь" или "Что ты можешь?". Чтобы завершить работу с "Сетевым городом" напишите "на этом все".' \
                                   ' А сейчас напишите пароль от Вашего аккаунта в "Сетевом городе".'

                    res['response']['text'] = alisa_answer

                    return

                sessionStorage[user_id]['password'] = user_answer
                alisa_answer = 'Отлично! А сейчас я попробую подключиться к серверам "Сетевого города". ' \
                               'Переспросите меня через несколько секунд, я вхожу в транс в поисках' \
                               ' Ваших оценок и заданий.'
                res['response']['text'] = alisa_answer
                sessionStorage[user_id]['authorisation'] = False

                res['response']['buttons'] = [
                    {
                        'title': 'Подождите',
                        'hide': True
                    },
                    {
                        'title': 'Ну подождите',
                        'hide': True
                    },
                    {
                        'title': 'Ну подождите чуть-чуть',
                        'hide': True
                    },
                    {
                        'title': 'Ну пожалуйста!',
                        'hide': True
                    }
                ]

                data = [
                    sessionStorage[user_id]['login'], sessionStorage[user_id]['password'],
                    sessionStorage[user_id]['region'], sessionStorage[user_id]['city'],
                    sessionStorage[user_id]['school']
                ]

                reload(user_id, data)  #
                # Функция должна обновлять базу данных
                return

        if sessionStorage[user_id]['connection'][0] is False:  # Если нет подключения
            if sessionStorage[user_id]['connection'][2] == 'waiting':
                alisa_answer = 'Я все еще подключаюсь! Подождите чуть-чуть!'
                res['response']['text'] = alisa_answer
                return

            if sessionStorage[user_id]['connection'][1] == 'new_account':
                alisa_answer = 'Что-то пошло не так! Я не могу подключиться к Вашему дневнику. ' \
                               'Проверьте правильность введенных данных или повторите позднее!'
                res['response']['text'] = alisa_answer
                sessionStorage[user_id]['login'] = None
                sessionStorage[user_id]['password'] = None  # Обнуляем настройки.
                sessionStorage[user_id]['authorisation'] = True
                return

            else:
                alisa_answer = 'Что-то пошло не так! Я не могу подключиться к Вашему дневнику.' \
                               ' Повторите попытку позже!'
                sessionStorage[user_id]['connection'][0] = 'remake'
                res['response']['text'] = alisa_answer
                return

        if sessionStorage[user_id]['connection'][0] is True:
            sessionStorage[user_id]['connection'][0] = 'connected'
            alisa_answer = 'Подключение прошло успешно! Спрашивайте, что Вы хотите узнать.'
            res['response']['text'] = alisa_answer
            return

        if sessionStorage[user_id]['connection'][0] == 'remake':
            for word in logout:
                if word in user_answer:
                    alisa_answer = 'Выход из системы проведен успешно. Теперь введите логин и пароль от того' \
                                   ' аккаунта, к которому Вы сейчас хотите подключиться.'
                    res['response']['text'] = alisa_answer

                    sessionStorage[user_id]['connection'] = []
                    sessionStorage[user_id]['region'] = None
                    sessionStorage[user_id]['city'] = None
                    sessionStorage[user_id]['school'] = None
                    sessionStorage[user_id]['login'] = None
                    sessionStorage[user_id]['password'] = None  # Приводим к стартовым настройкам
                    sessionStorage[user_id]['authorisation'] = True
                    return

            alisa_answer = 'Я вновь собираю информацию с Вашего аккаунта. Подождите чуть-чуть, пожалуйста.'
            res['response']['text'] = alisa_answer
            reload(user_id, [])
            return

        if sessionStorage[user_id]['connection'][0] == 'connected':

            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': False
                },
                {
                    'title': 'На этом все',
                    'hide': False
                }
            ]

            if 'помощь' in user_answer or 'помоги' in user_answer or 'что ты можешь' in user_answer:
                alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                               ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                               ' четвертей.' \
                               ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                               ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                               ' попросите меня выйти из Вашего аккаунта. Чтобы завершить работу с "Сетевым городом" напишите "на этом все".'

                res['response']['text'] = alisa_answer
                return

            for word in logout:
                if word in user_answer:
                    alisa_answer = 'Выход из системы проведен успешно. Теперь введите логин и пароль от того' \
                                   ' аккаунта, к которому Вы сейчас хотите подключиться.'
                    res['response']['text'] = alisa_answer

                    sessionStorage[user_id]['connection'] = ['connected', 'old_account', 'waiting']
                    sessionStorage[user_id]['region'] = None
                    sessionStorage[user_id]['city'] = None
                    sessionStorage[user_id]['school'] = None
                    sessionStorage[user_id]['login'] = None
                    sessionStorage[user_id]['password'] = None  # Приводим к стартовым настройкам.
                    sessionStorage[user_id]['authorisation'] = True

                    User.delete(User.query.filter_by(user_id=user_id).first())  # Удаляем из базы данных старые данные.
                    return

            for word in reconnect:  # Обновление базы данных
                if word in user_answer:
                    alisa_answer = 'Я вновь собираю информацию с Вашего аккаунта. Подождите чуть-чуть, пожалуйста.'
                    res['response']['text'] = alisa_answer
                    User.delete(User.query.filter_by(user_id=user_id).first())  # Удаляем из базы данных старые данные.
                    reload(user_id, [])
                    return

            for skill in skills:
                for word in skills[skill]:
                    if word in user_answer:
                        alisa_answer = get_info(user_id, skill, user_answer)
                        res['response']['text'] = alisa_answer
                        return

        alisa_answer = 'Увы, я не понимаю то, что Вы говорите. Попробуйте сформулировать по-другому.'
        res['response']['text'] = alisa_answer
        return

    def get_info(user_id, skill, user_answer):
        print(user_id)

        if skill == 'Total marks':
            return 'Здарова, это итоги четвертей. Организуем.'
        elif skill == 'The last homework':
            for lesson in lessons:
                for word in lessons[lesson]:
                    if word in user_answer:
                        return 'Последнее дз по ' + lesson
        elif skill == 'Average mark':
            for lesson in lessons:
                for word in lessons[lesson]:
                    if word in user_answer:
                        return 'Средняя оценка по ' + lesson
        elif skill == 'All marks':
            for lesson in lessons:
                for word in lessons[lesson]:
                    if word in user_answer:
                        return 'Оценки по ' + lesson
        elif skill == 'The table':
            return 'Здарова, это таблица с предметами. Организуем.'

        return 'Увы, я не понимаю то, что Вы говорите. Попробуйте сформулировать по-другому.'

    def reload(user_id, data):  # Загрузка данных пользователя в базу данных.
        if data:
            result = handle(user_id, data)
            if result:
                User.add(user_id=user_id, login=data[0], password=data[1],
                         region_id=data[2], city_id=data[3], school_id=data[4])
                sessionStorage[user_id]['connection'] = [False, 'new_account', 'waiting']
                return

            sessionStorage[user_id]['connection'] = [False, 'new_account', 'failed']
            return

        else:  # Если без data - значит данные уже хранятся в db
            data = [sessionStorage[user_id]['login'], sessionStorage[user_id]['password'],
                    sessionStorage[user_id]['region'], sessionStorage[user_id]['city'],
                    sessionStorage[user_id]['school']]
            result = handle(user_id, data)
            if result:
                User.add(user_id=user_id, login=data[0], password=data[1],
                         region_id=data[2], city_id=data[3], school_id=data[4])
                sessionStorage[user_id]['connection'] = [False, 'old_account', 'waiting']
                return

            sessionStorage[user_id]['connection'] = [False, 'old_account', 'failed']
            return

    def handle(user_id, user_info):
        url = 'http://127.0.0.1:8080/connect?login={}&password={}&schoolid={}&user_id={}'.format(user_info[0],
                                                                                                 user_info[1],
                                                                                                 user_info[4], user_id)
        response = requests.get(url).text
        result = eval(response)  # Перевод строки в json
        if result == {'10006': 'Invalid login or password'}:
            return False

        return True
