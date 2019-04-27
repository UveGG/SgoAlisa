from flask import Flask, request
import requests
from xml.etree import ElementTree


app = Flask(__name__)


@app.route("/connect")
def connect():
    login = request.args.get('login', default='мПетроваЛ20')
    password = request.args.get('password', default='Л631963')
    school = request.args.get('school', default='444')
    user_id = request.args.get('school', default='444')
    url = 'https://sgo2test.ir-tech.ru/api/lacc.asp?Function=Login3&SchoolID=' + \
          school + '&Login=' + login + '&Password=' + password
    response = requests.get(url)
    result = format_info(response)
    print(result)
    return str(result)


def format_info(response):
    tree = ElementTree.fromstring(response.content)
    a = None
    branches = tree

    wiki = {}
    for branch in branches:
        deep_xms(branch, wiki, a)
    wiki.__delitem__(None)
    return wiki


def deep_xms(items, wiki, a):
    for item in items:
        try:
            wiki[a] = item.text.encode('ISO-8859-1').decode('windows-1251')
            a = item.text.encode('ISO-8859-1').decode('windows-1251')
        except Exception:
            deep_xms(item, wiki, a)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
