import uuid

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from resource.models import UserModel
from services.email.email_service import SendEmail
from services.redis.redis_services import RedisService

parser = reqparse.RequestParser()


class UserRegistration(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('password', help='This field cannot be blank')
    parser.add_argument('email', help='This field cannot be blank')

    def post(self):
        data = parser.parse_args()
        redis = RedisService()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}, 401

        if len(data['password']) < 8:
            return {'message': 'password length should be more than 8 characters'}, 401

        salt = bcrypt.gensalt().decode("utf-8")
        new_user = UserModel(
            username=data['username'],
            email=data['email'],
            group='user',
            salt=salt,
            password=UserModel.generate_hash(data['password'] + salt),
            status=False
        )

        token = uuid.uuid4()
        redis.write(data['username'], token)

        SendEmail.send_main('account_verification', data['email'], token)
        try:
            new_user.save_to_db()
            return {
                'message': 'User {} was created, check your mailbox to activate the user.'.format(data['username'])}
        except:
            return {'message': 'Something went wrong'}, 500


# ------------------------------------------------------------------------
class UserLogin(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('password', help='This field cannot be blank')

    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        if not current_user.status:
            return {'message': 'User {} has not been activeted'.format(data['username'])}

        if UserModel.verify_hash(data['password'] + current_user.salt, current_user.password):
            access_token = create_access_token(identity={"username": data['username'], "group": current_user.group})
            refresh_token = create_refresh_token(identity={"username": data['username'], "group": current_user.group})
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}, 401


# -----------------------------------------------------------------------------
class UserActivation(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('token', help='This field cannot be blank')

    def put(self):
        data = parser.parse_args()
        redis = RedisService()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        valid_token = redis.read(data['username'])

        if valid_token == data['token']:
            UserModel.update_status(data['username'], True)
            redis.delete_key(data['username'])
            return {'message': 'User {} activated'.format(data['username'])}
        else:
            return {'message': 'Token is invalid'}, 401


# ------------------------------------------------------------------------
class UserResetPassword(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('token', help='This field cannot be blank')
    parser.add_argument('password', help='This field cannot be blank')

    def post(self):
        data = parser.parse_args()
        redis = RedisService()

        token = uuid.uuid4()

        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}, 401

        redis.write(data['username'], token)
        SendEmail.send_main('reset_password', current_user.email, token)
        return {'message': 'Please check your mailbox'}

    def put(self):
        data = parser.parse_args()

        if len(data['password']) < 8:
            return {'message': 'password length should be more than 8 characters'}, 401

        redis = RedisService()
        valid_token = redis.read(data['username'])

        if valid_token == data['token']:
            user = UserModel.find_by_username(data['username'])
            password = UserModel.generate_hash(data['password'] + user.salt)
            UserModel.update_password(data['username'], password)
            redis.delete_key(data['username'])
            return {'message': 'User {} pasword reseted'.format(data['username'])}
        else:
            return {'message': 'Token is invalid'}, 401


# ------------------------------------------------------------------------
class AdminAddToGroup(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('group', help='This field cannot be blank')

    @jwt_required()
    def post(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        if token["group"] == "admin":
            user = UserModel.find_by_username(data["username"])
            if user:
                UserModel.admin_add_to_group(data["username"], data["group"])
                return {'message': 'users add to entered group successfully'}
            else:
                return {'message': 'this users not exist'}
        else:
            return {'message': 'you have not access to this api'}


# ---------------------------------------------------------------------------
class AdminCreateAdmin(Resource):
    parser.add_argument('username', help='This field cannot be blank')
    parser.add_argument('password', help='This field cannot be blank')

    @jwt_required()
    def post(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        if token["group"] == "admin":
            user = UserModel.find_by_username(data["username"])
            if user:
                return {'message': 'this users already exist'}
            else:
                salt = bcrypt.gensalt().decode("utf-8")
                new_user = UserModel(
                    username=data['username'],
                    group='admin',
                    salt=salt,
                    password=UserModel.generate_hash(data['password'] + salt)
                )
                new_user.save_to_db()
                access_token = create_access_token(identity={"username": data['username'], "group": "users"})
                refresh_token = create_refresh_token(identity={"username": data['username'], "group": "users"})
                return {
                    'message': 'User {} was created'.format(data['username']),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
        else:
            return {'message': 'you have not access to this api'}
