from dbase import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(1000), nullable=False)

    login = db.Column(db.String(1000), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<User {} {} {} {}>'.format(
            self.id,
            self.login,
            self.password,
            self.user_id

        )

    @staticmethod
    def add(user_id, login, password):
        user = User(
            user_id=user_id,
            login=login,
            password=password
        )
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()


class Lesson(db.Model):
        id_of_lesson = db.Column(db.Integer, primary_key=True)
    
        user_id = db.Column(db.Integer, primary_key=True)
    
        average_mark = db.Column(db.String(1000), nullable=False)
    
        all_marks = db.Column(db.String(1000), nullable=False)
    
        homework = db.Column(db.String(1000), nullable=False)
    
        def __repr__(self):
            return '<Lesson >'.format(
                self.id,
                self.login,
                self.password,
                self.user_id
    
            )
    
        @staticmethod
        def add(user_id, average_mark, all_marks, homework):
            lesson = Lesson(
                user_id=user_id,
                average_mark=average_mark,
                all_marks=all_marks,
                homework=homework)
            db.session.add(lesson)
            db.session.commit()
    
        @staticmethod
        def delete(lesson):
            db.session.delete(lesson)
            db.session.commit()
