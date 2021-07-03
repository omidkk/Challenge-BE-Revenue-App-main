from passlib.hash import pbkdf2_sha256 as sha256

from application import db


# --------------------------------users----------------------------------
class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    salt = db.Column(db.String(120), nullable=False)
    group = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def admin_add_to_group(cls, username, group):
        item = cls.query.filter_by(username=username).first()
        item.group = group
        db.session.commit()

    @classmethod
    def update_status(cls, username, status):
        user = db.session.query(cls).filter(cls.username == username).first()
        user.status = status
        db.session.commit()
        return {'message': 'item updated successfully '}

    @classmethod
    def update_password(cls, username, password):
        user = db.session.query(cls).filter(cls.username == username).first()
        user.password = password
        db.session.commit()
        return {'message': 'item updated successfully '}

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                "id": x.id,
                'username': x.username,
                'email': x.email,
                'password': x.password,
                "salt": x.salt,
                "group": x.group,
                "status": x.status
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_by_username(cls, username):
        db.session.query(cls).filter(cls.username == username).delete()
        db.session.commit()
        return {'message': 'item deleted successfully '}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


# --------------------------------company----------------------------------
class CompanyModel(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    branch_number = db.Column(db.String(120), unique=True, nullable=False)
    company_name = db.Column(db.String(120), unique=True, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, company_id):
        return cls.query.filter_by(id=company_id).first()

    @classmethod
    def find_by_branch_number(cls, company_branch_number):
        return cls.query.filter_by(branch_number=company_branch_number).first()

    @classmethod
    def delete_by_id(cls, id):
        db.session.query(cls).filter(cls.id == id).delete()
        db.session.commit()
        return {'message': 'item deleted successfully '}

    @classmethod
    def update_by_id(cls, id, update):
        company = db.session.query(cls).filter(cls.id == id).first()
        company.company_name = update
        db.session.commit()
        return {'message': 'item updated successfully '}

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                "id": x.id,
                'company_name': x.company_name,
            }

        return {'companies': list(map(lambda x: to_json(x), CompanyModel.query.all()))}


# --------------------------------company_day----------------------------------
class CompanyDailyModel(db.Model):
    __tablename__ = 'company_daily'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    date = db.Column(db.String(120), unique=False, nullable=False)
    total = db.Column(db.Float, unique=False, nullable=False, default=0)
    company_name = db.relationship('CompanyModel', backref='companies')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_company_id(cls, company_id):
        return cls.query.filter_by(company_id=company_id).all()

    @classmethod
    def find_by_company_id_and_date(cls, company_id, date):
        return cls.query.filter_by(company_id=company_id, date=date).first()

    @classmethod
    def update_company_daily(cls, id, total):
        company_daily = db.session.query(cls).filter(cls.id == id).first()
        company_daily.total += total
        db.session.commit()
        return {'message': 'item updated successfully '}

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                "id": x.id,
                'company_daily': x.company_name,
                'date': x.date,
                'total': x.total,
            }

        return {'company_daily': list(map(lambda x: to_json(x), CompanyDailyModel.query.all()))}


# --------------------------------company_hourly----------------------------------
class CompanyHourlyModel(db.Model):
    __tablename__ = 'company_hourly'

    id = db.Column(db.Integer, primary_key=True)
    company_daily_id = db.Column(db.Integer, db.ForeignKey('company_daily.id'))
    hour = db.Column(db.String(120), unique=False, nullable=False)
    total = db.Column(db.Float, unique=False, nullable=False, default=0)
    company_date = db.relationship('CompanyDailyModel', backref='company_daily')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_company_daily_id(cls, company_daily_id):
        return cls.query.filter_by(company_daily_id=company_daily_id).all()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                "id": x.id,
                'company_daily_id': x.company_daily_id,
                'hour': x.hour,
                'total': x.total,

            }

        return {'company_hour': list(map(lambda x: to_json(x), CompanyHourlyModel.query.all()))}
