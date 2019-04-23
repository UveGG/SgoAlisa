from flask import request
import logging
import json

from models import User


def init_route(app, db):

    logging.basicConfig(level=logging.INFO)

    skills = {
        'Total marks': [
            'итог'
        ],

        'The table': [
            'табли'
        ],

        'The last homework': [
            'дз',
            'дом',
            'домашнее задание',
            'задали',
            'задала',
            'что по',
            'домашка',
            'домашке',
            'домашку',
            'homework'
        ],

        'Average mark': [
            'средн',
        ],

        'All marks': [
            'все',
            'оценк'
        ]
    }

    sessionStorage = {}

    lessons = {
        'english': [
            'английский',
            'английскому',
            'англичанский',
            'англичанскому',
            'англ',
            'англу',
            'англичанка',
        ],

        'german': [
            'немецкий',
            'немецкому',
            'немчанка',
            'немцу',
            'немецу',
        ],

        'french': [
            'французский',
            'французскому',
            'француский',
            'францускому',
            'французкий',
            'французкому',
            'францу',
            'француженка',
            'франциха',
            'франка',
        ],

        'russian': [
            'русский',
            'руский',
            'русскому',
            'рускому',
            'русу',
            'русиш',
            'русишу',
            'русо',
            'руском',
            'русском',
            'русский'
        ],

        'literature': [
            'литература',
            'литературе',
            'литра',
            'литре',
            'литер',
            'литеру',
            'литераторша'
        ],

        'main_language': [
            'родной'
        ],

        'main_literature': [
            'родная'
        ],

        'maths': [
            'математика',
            'математике',
            'матеша',
            'матеше',
            'матика',
            'матике',
        ],

        'geometry': [
            'геометрия',
            'геометрии',
            'геома',
            'геоме',
        ],

        'algebra': [
            'алгебра',
            'алгебре',
            'алге'
        ],

        'geography': [
            'география',
            'географии',
            'геогр'
        ],

        'biology': [
            'био',
        ],

        'chemist': [
            'хими'
        ],

        'physics': [
            'физи'
        ],

        'physical_educal': [
            'физк',
            'физр',
            'физ-р'
        ],

        'technology': [
            'техн'
        ],

        'obzh': [
            'обж'
        ],

        'art': [
            'изо',
            'рисование'
        ],

        'drawing': [
            'черч',
            'черт'
        ],

        'world_history': [
            'мировая ист',
            'мировой ист',
            'мир ист'
        ],

        'russian_history': [
            'ист'
        ],

        'society': [
            'общ'
        ],

        'it': [
            'икт',
            'инф'
        ],

        'ops': [
            'опс'
        ]

    }

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

        if user_id not in sessionStorage:
            sessionStorage[user_id] = {}
            sessionStorage[user_id]['connection'] = 'waiting'
            sessionStorage[user_id]['login'] = None
            sessionStorage[user_id]['password'] = None
            sessionStorage[user_id]['authorisation'] = False

        if req['session']['new']:
            alisa_answer = 'Привет! Это моё умение предназначено для помощи школьнику и его родителям. ' \
                                      'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                      ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                      ' четвертей.'

            if not User.query.filter_by(user_id=user_id).first():
                sessionStorage[user_id]['authorisation'] = True
                alisa_answer += ' Сначала скажите Ваш логин и пароль для входа в "Сетевой Город", ' \
                                'чтобы мне было с чем работать (первым сообщением скажите логин, а вторым - пароль).'
            else:
                reload(user_id, [])
            res['response']['text'] = alisa_answer
            return

        if sessionStorage[user_id]['authorisation']:
            if sessionStorage[user_id]['login'] is None:
                if 'помощь' in user_answer or 'помогите' in user_answer or 'документация' in user_answer:
                    alisa_answer = 'Напишите Ваш логин для входа в "Сетевой Город".'
                    res['response']['text'] = alisa_answer
                    return

                sessionStorage[user_id]['login'] = user_answer

                alisa_answer = 'Отлично! А теперь скажите Ваш пароль для входа в "Сетевой город".'
                res['response']['text'] = alisa_answer
                return

            if sessionStorage[user_id]['password'] is None:
                if 'помощь' in user_answer or 'помогите' in user_answer or 'документация' in user_answer:
                    alisa_answer = 'Напишите Ваш пароль для входа в "Сетевой Город".'
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

        elif not sessionStorage[user_id]['connection'][0]:  # Если нет подключения
            if sessionStorage[user_id]['connection'][2] == 'waiting':
                alisa_answer = 'Я все еще подключаюсь! Подождите чуть-чуть!'
                res['response']['text'] = alisa_answer
                return

            if sessionStorage[user_id]['connection'][1] == 'new_account':
                alisa_answer = 'Что-то пошло не так! Я не могу подключиться к Вашему дневнику. ' \
                                   'Проверьте правильность введенных данных или повторите позднее!'
                res['response']['text'] = alisa_answer
                sessionStorage[user_id]['login'] = None
                sessionStorage[user_id]['password'] = None
                sessionStorage[user_id]['authorisation'] = True
                return

            else:
                alisa_answer = 'Что-то пошло не так! Я не могу подключиться к Вашему дневнику.' \
                               ' Повторите попытку похже!'
                res['response']['text'] = alisa_answer
                return

        elif sessionStorage[user_id]['connection'][0] == True:
            sessionStorage[user_id]['connection'] = 'connected'

            alisa_answer = 'Подключение прошло успешно! Спрашивайте, что Вы хотите узнать.'
            res['response']['text'] = alisa_answer
            return

        if sessionStorage[user_id]['connection'] == 'connected':
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

    def reload(user_id, data):
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
            sessionStorage[user_id]['connection'] = [result[0], result[1],
                                                     result[2]]
            return
