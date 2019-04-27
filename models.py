from dbase import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(1000), nullable=False)

    login = db.Column(db.String(1000), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)

    region_id = db.Column(db.Integer, nullable=False)

    city_name = db.Column(db.String(1000), nullable=False)
    city_id = db.Column(db.Integer, nullable=False)

    school_name = db.Column(db.String(1000), nullable=False)
    school_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User {} {} {} {} {} {} {}>'.format(
            self.id,
            self.login,
            self.password,
            self.user_id,
            self.region_id,
            self.city_id,
            self.school_id

        )

    @staticmethod
    def add(user_id, login, password, region_id, city_id, school_id):
        user = User(
            user_id=user_id,
            login=login,
            password=password,
            region_id=region_id,
            city_id=city_id,
            school_id=school_id

        )
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    regionid = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Region {} {}>'.format(
            self.id,
            self.regionid
        )

    @staticmethod
    def add(regionid):
        region = Region(regionid=regionid)

        db.session.add(region)
        db.session.commit()

    @staticmethod
    def delete(region):
        db.session.delete(region)
        db.session.commit()


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, nullable=False)

    cityid = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<City {} {} {}>'.format(
            self.id,
            self.name,
            self.cityid
        )

    @staticmethod
    def add(cityid, name, region_id):
        city = City(cityid=cityid,
                    name=name, region_id=region_id)
        db.session.add(city)
        db.session.commit()

    @staticmethod
    def delete(city):
        db.session.delete(city)
        db.session.commit()


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, nullable=False)

    schoolid = db.Column(db.Integer, nullable=False)

    name = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<School {} {} {}>'.format(
            self.id,
            self.name,
            self.schoolid
        )

    @staticmethod
    def add(schoolid, name, city_id):
        school = School(schoolid=schoolid,
                        name=name, city_id=city_id)
        db.session.add(school)
        db.session.commit()

    @staticmethod
    def delete(school):
        db.session.delete(school)
        db.session.commit()
