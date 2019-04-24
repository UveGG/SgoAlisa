from flask import request
import logging
import json
from requests_sorting import lessons, skills, logout, reconnect
from models import User


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
            alisa_answer = 'Привет! Это моё умение предназначено для помощи школьнику и его родителям. ' \
                                      'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                      ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                      ' четвертей. Всю эту информацию я беру с сайта "Сетевой город. Образование"' \
                                      ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                      ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                      ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                      ' "помощь" или "Что ты можешь?".'

            if not User.query.filter_by(user_id=user_id).first():
                sessionStorage[user_id] = {}
                sessionStorage[user_id]['connection'] = [False, 'new_account', 'waiting']
                sessionStorage[user_id]['login'] = None
                sessionStorage[user_id]['password'] = None
                sessionStorage[user_id]['authorisation'] = True
                alisa_answer += ' Но сначала скажите Ваш логин и пароль для входа в "Сетевой Город", ' \
                                'чтобы мне было с чем работать (первым сообщением скажите логин, а вторым - пароль).'
            else:
                user = User.query.filter_by(user_id=user_id).first()

                sessionStorage[user_id] = {}
                sessionStorage[user_id]['login'] = user.login
                sessionStorage[user_id]['password'] = user.password
                sessionStorage[user_id]['connection'] = ['connected', 'old_account', 'waiting']
                sessionStorage[user_id]['authorisation'] = False

                alisa_answer += ' А сейчас я обновляю базу данных. Подождите чуть-чуть, пожалуйста!'

                User.delete(User.query.filter_by(user_id=user_id).first())
                reload(user_id, [])  # Обновление базы данных

            res['response']['text'] = alisa_answer
            return

        # noinspection PySimplifyBooleanCheck
        logging.warning(str(sessionStorage[user_id]['authorisation']) * 340)
        if sessionStorage[user_id]['authorisation']:
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
                                      ' "Помощь" или "Что ты можешь?". А сейчас напишите логин от Вашего аккаунта в "Сетевом городе".'

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
                                      ' "Помощь" или "Что ты можешь?". А сейчас напишите пароль от Вашего аккаунта в "Сетевом городе".'

                    res['response']['text'] = alisa_answer
                    return

                sessionStorage[user_id]['password'] = user_answer
                alisa_answer = 'Отлично! А сейчас я попробую подключиться к серверам "Сетевого города". ' \
                               'Переспросите меня через несколько секунд, я вхожу в транс в поисках' \
                               ' Ваших оценок и заданий.'
                res['response']['text'] = alisa_answer
                sessionStorage[user_id]['authorisation'] = False
                reload(user_id, [sessionStorage[user_id]['login'],
                                 sessionStorage[user_id]['password']])  #
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

                User.delete(User.query.filter_by(user_id=user_id).first())  # Удаляем из базы данных старые данные.
                return

            else:
                alisa_answer = 'Что-то пошло не так! Я не могу подключиться к Вашему дневнику.' \
                               ' Повторите попытку похже!'
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

                    sessionStorage[user_id]['connection'] = ['connected', 'old_account', 'waiting']
                    sessionStorage[user_id]['login'] = None
                    sessionStorage[user_id]['password'] = None  # Приводим к стартовым настройкам
                    sessionStorage[user_id]['authorisation'] = True

                    User.delete(User.query.filter_by(user_id=user_id).first())  # Удаляем из базы данных старые данные.
                    return

            reload(user_id, [])

        if sessionStorage[user_id]['connection'][0] == 'connected':
            if 'помощь' in user_answer or 'помоги' in user_answer or 'что ты можешь' in user_answer:
                    alisa_answer = 'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                      ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                      ' четвертей.' \
                                      ' Для обновления моей информации о Вашем дневнике напишите "обновись", "обнови информацию",' \
                                      ' "перезайди в дневник" или что-то в этом духе. Чтобы я забыла Ваши логин и пароль' \
                                      ' попросите меня выйти из Вашего аккаунта. Чтобы перечитать мои возможности напишите' \
                                      ' "Помощь" или "Что ты можешь?".'

                    res['response']['text'] = alisa_answer
                    return

            for word in logout:
                if word in user_answer:
                    alisa_answer = 'Выход из системы проведен успешно. Теперь введите логин и пароль от того' \
                                   ' аккаунта, к которому Вы сейчас хотите подключиться.'
                    res['response']['text'] = alisa_answer

                    sessionStorage[user_id]['connection'] = ['connected', 'old_account', 'waiting']
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
                        return lesson
        elif skill == 'Average mark':
            for lesson in lessons:
                for word in lessons[lesson]:
                    if word in user_answer:
                        return lesson
        elif skill == 'All marks':
            for lesson in lessons:
                for word in lessons[lesson]:
                    if word in user_answer:
                        return lesson
        elif skill == 'The table':
            return 'Здарова, это таблица с предметами. Организуем.'

        return 'Увы, я не понимаю то, что Вы говорите. Попробуйте сформулировать по-другому.'

    def reload(user_id, data):  # Загрузка данных пользователя в базу данных.
        # result = [Обновилось ли, старый или новый аккаунт, причина необновления] - результат загрузки базы данных
        if data:
            result = [True, 'new_account', 'failed']

            if result[0]:
                User.add(user_id=user_id, login=data[0], password=data[1])

            sessionStorage[user_id]['connection'] = [result[0], result[1],
                                                     result[2]]
            return
            # Подключаемся к серверам сетевого города. В случае успеха
            # заносим данные в базу данных.
            # Если нет - возвращаем список [False, 'waiting'], если не успели
            # И [False, 'failed'], если не смогли.
        else:
            result = [True, 'old_account', 'failed']
            if result[0]:
                User.add(user_id=user_id, login=sessionStorage[user_id]['login'],
                         password=sessionStorage[user_id]['password'])

            sessionStorage[user_id]['connection'] = [result[0], result[1],
                                                     result[2]]
            return
