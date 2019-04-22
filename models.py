from dbase import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    id_for_alice = db.Column(db.String(1000), nullable=False)

    login = db.Column(db.String(1000), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<User {} {} {} {}>'.format(
            self.id,
            self.login,
            self.password,
            self.id_for_alice

        )

    @staticmethod
    def add(login, password, id_for_alice):
        user = User(
            id_for_alice=id_for_alice,
            login=login,
            password=password
        )
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()
