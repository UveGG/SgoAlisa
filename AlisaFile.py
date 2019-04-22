from flask import Flask, request
import logging
import json
from dbase import db

app = Flask(__name__)

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

    if req['session']['new']:
        res['response']['text'] = 'Привет! Это моё умение предназначено для помощи школьнику и его родителям. ' \
                                  'Я могу подсказать последнее домашнее задание или вывести таблицу из отчетов,' \
                                  ' сказать средний балл или перечислить оценки по предмету, подвести итоги' \
                                  ' четвертей. Сначала скажи свой логин и пароль для входа в "Сетевой Город",' \
                                  ' чтобы мне было с чем работать.'

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


if __name__ == '__main__':
    app.run()
