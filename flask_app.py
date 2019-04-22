from flask import Flask
from AlisaFile import init_route
from dbase import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'kyXchNb6A3VhCFoBBuCOaCP1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://UveGG:4338437233SP@UveGG.mysql.pythonanywhere-services.com/UveGG$SgoDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
init_route(app, db)

if __name__ == '__main__':
    app.run()
