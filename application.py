from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)

# set FLASK_DEBUG=1 in command line
# set FLASK_ENV=development
# set FLASK_APP=application.py

application.config['ENV'] = 'development'
application.config['DEBUG'] = True
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SECRET_KEY'] = 'some-secret-string'
application.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

db = SQLAlchemy(application)
migrate = Migrate(application, db)

jwt = JWTManager(application)


@application.before_first_request
def create_tables():
    db.create_all()


api = Api(application)
import views
from resource import models
from services.users import user_services
from services.topics import topic_services

api.add_resource(user_services.UserRegistration, '/registration')
api.add_resource(user_services.UserLogin, '/login')
api.add_resource(user_services.AdminAddToGroup, '/admin/add_To_group')
api.add_resource(user_services.AdminCreateAdmin, '/user/create/admin')
api.add_resource(user_services.UserActivation, '/user/activate')
api.add_resource(user_services.UserResetPassword, '/user/forgetPassword')

api.add_resource(topic_services.CreateTopic, '/createTopic')
api.add_resource(topic_services.CreateTopicOptions, '/createTopicOptions')
api.add_resource(topic_services.GetTopicNames, '/topicNames')
api.add_resource(topic_services.GetAllTopicOptions, '/topicsOptions')
api.add_resource(topic_services.GetSpecificTopicOptions, '/SpecificTopicsOptions')
api.add_resource(topic_services.GetSpecificTopicOptionsResults, '/SpecificTopicsOptionsResult')
api.add_resource(topic_services.GetAllTopicsOptionsResults, '/AllTopicsOptionsResult')
api.add_resource(topic_services.ChooseOption, '/ChooseOption')
api.add_resource(topic_services.AdminDeleteTopicByid, '/topic/delete')
api.add_resource(topic_services.AdminUpdateSurveyTopic, '/topic/update')
api.add_resource(topic_services.AdminUpdateSurveyTopicOptions, '/topicOption/update')

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
