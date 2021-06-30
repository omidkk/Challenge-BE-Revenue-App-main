import json
from collections import defaultdict

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse

from resource.models import TopicModel, TopicOptionModel, UserAnswerTrackModel

parser = reqparse.RequestParser()


class CreateTopic(Resource):
    parser.add_argument('topic', help='This field cannot be blank')

    @jwt_required()
    def post(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        if token["group"] == "admin":
            new_topic = TopicModel(
                topic_name=data['topic'],
            )

            try:
                new_topic.save_to_db()
                return {
                    'message': 'Topic {} was created'.format(data['topic']),
                }
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            return {'message': 'you have not access to this api'}, 401


# -----------------------------------------------------------------------------

class CreateTopicOptions(Resource):
    parser.add_argument('options', action='append', help='This field cannot be blank')
    parser.add_argument('key', help='This field cannot be blank')

    @jwt_required()
    def post(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        if not data['options']:
            return {'message': 'No option found'}, 404

        if not TopicModel.find_by_id(data['key']):
            return {'message': 'Topic id not found'}, 404

        if token["group"] == "admin":
            try:
                for option in data['options']:
                    new_topic_option = TopicOptionModel(
                        option=option,
                        key=data["key"],
                        result=0
                    )

                    new_topic_option.save_to_db()
                status = ''
                for option in data['options']:
                    status += 'Option {} was created\n'.format(option)
                return {'message': status}
            except:
                return {'message': 'Something went wrong'}, 500
        else:
            return {'message': 'you have not access to this api'}, 401


# -----------------------------------------------------------------------------

class GetTopicNames(Resource):
    @jwt_required()
    def get(self):
        token = get_jwt_identity()
        return TopicModel.return_all()


# -----------------------------------------------------------------------------

class GetAllTopicOptions(Resource):
    @jwt_required()
    def get(self):
        token = get_jwt_identity()
        if token["group"] == "admin":
            return TopicOptionModel.return_all()
        else:
            return {'message': 'you have not access to this api'}, 401


# -----------------------------------------------------------------------------

class GetSpecificTopicOptions(Resource):
    parser.add_argument('id', help='This field cannot be blank')

    @jwt_required()
    def get(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        topics_with_options = TopicOptionModel.find_by_topic(data['id'])
        result = {'topic': str,
                  'topic_id': str,
                  'options': list()}
        if topics_with_options:
            for topics_with_option in topics_with_options:
                result['topic'] = topics_with_option.topic_name.topic_name
                result['topic_id'] = data['id']
                result['options'].append({topics_with_option.option: topics_with_option.id})

            return result
        else:
            return {'message': 'Topic does not have any options'}


# -----------------------------------------------------------------------------

class GetSpecificTopicOptionsResults(Resource):
    parser.add_argument('id', help='This field cannot be blank')

    @jwt_required()
    def get(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        topics_with_options = TopicOptionModel.find_by_topic(data['id'])
        result = {'topic': str,
                  'options': list()}
        for topics_with_option in topics_with_options:
            result['topic'] = topics_with_option.topic_name.topic_name
            result['options'].append({topics_with_option.option: topics_with_option.result})

        return result


# -----------------------------------------------------------------------------

class GetAllTopicsOptionsResults(Resource):
    @jwt_required()
    def get(self):
        token = get_jwt_identity()
        topics_with_options = TopicOptionModel.return_all()['topic_options']
        result = defaultdict(list)
        for topics_with_option in topics_with_options:
            result[topics_with_option["topic"]].append({topics_with_option['option']: topics_with_option['result']})

        return result


# -----------------------------------------------------------------------------

class ChooseOption(Resource):
    parser.add_argument('topic_id', help='This field cannot be blank')
    parser.add_argument('option_id', help='This field cannot be blank')

    @jwt_required()
    def post(self):
        token = get_jwt_identity()
        data = parser.parse_args()
        try:
            user_answers = UserAnswerTrackModel.find_by_topic_option_username(data['topic_id'], token['username'])
            if not user_answers:
                topic_with_options = TopicOptionModel.find_by_topic_id_option_id(data['topic_id'], data['option_id'])
                topic_with_options.result += 1
                user_answer = UserAnswerTrackModel(username=token['username'], topic_id=data['topic_id'])

                user_answer.save_to_db()
                topic_with_options.save_to_db()
                return {'message': 'Answer submitted'}

            else:
                return {'message': 'User already answered this topic'}, 500
        except:
            return {'message': 'Something went wrong'}, 500


# -----------------------------------------------------------------------------

class AdminDeleteTopicByid(Resource):
    parser.add_argument('topic_id', help='This field cannot be blank')

    @jwt_required()
    def delete(self):
        token = get_jwt_identity()
        data = parser.parse_args()
        if token["group"] == "admin":
            TopicModel.delete_by_id(data["topic_id"])
            TopicOptionModel.delete_by_id(data["topic_id"])
            return {'message': 'Topic is deleted'}
        else:
            return {'message': 'you have not access to this api'}, 401


# -----------------------------------------------------------------------------

class AdminUpdateSurveyTopic(Resource):
    parser.add_argument('topic_id', help='This field cannot be blank')
    parser.add_argument('topic_name', help='This field cannot be blank')

    @jwt_required()
    def put(self):
        token = get_jwt_identity()
        data = parser.parse_args()
        if token["group"] == "admin":
            TopicModel.update_by_id(data["topic_id"], data["topic_name"])
            return {'message': 'Topic is updated'}
        else:
            return {'message': 'you have not access to this api'}, 401


# -----------------------------------------------------------------------------

class AdminUpdateSurveyTopicOptions(Resource):
    parser.add_argument('topic_id', help='This field cannot be blank')
    parser.add_argument('updates', help='This field cannot be blank')

    @jwt_required()
    def put(self):
        token = get_jwt_identity()
        data = parser.parse_args()
        update = json.loads(data["updates"].replace("'", '"'))
        if token["group"] == "admin":
            if TopicModel.find_by_id(update["topic_id"]):
                TopicOptionModel.update_by_id(data["option_id"], update)
            else:
                return {'message': 'Topic id is not available'}, 500
            return {'message': 'Topic is updated'}
        else:
            return {'message': 'you have not access to this api'}, 401
