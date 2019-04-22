from flask import Flask, request
import logging
import json


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}
lesson = {
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

    sessionStorage[user_id] = {
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

        'The last mark': [
            'hello'
        ],

        'Average mark': [

        ],

        'All marks': [

        ],

        'The table': [
            'vodka'
        ],

        'Total mark': [

        ]
    }

    if req['session']['new']:
        res['response']['text'] = 'Привет! Это моё умение предназначено для помощи школьнику и его родителям. ' \
                                  'Я могу подсказать последнее домашнее задание или оценку по какому-либо предмету,' \
                                  ' сказать средний балл, перечислить оценки или подвести итоги четверти. Сначала ' \
                                  'скажи свой логин и пароль для входа в "Сетевой Город", чтобы мне было с чем' \
                                  ' работать.'

        return

    for skill in sessionStorage[user_id]:
        for word in sessionStorage[user_id][skill]:
            if word in user_answer:
                alisa_answer = get_info(user_id, skill)
                res['response']['text'] = alisa_answer
                return

    alisa_answer = 'Увы, я не понимаю то, что Вы говорите. Попробуйте спросить по-другому.'
    res['response']['text'] = alisa_answer
    return


def get_info(user_id, skill):
    print(user_id)
    if skill == 'The table':
        return 'Здарова это водяра'
    elif skill == 'The last mark':
        return 'Привет зая'
    else:
        return 'Пока зая'


if __name__ == '__main__':
    app.run()
