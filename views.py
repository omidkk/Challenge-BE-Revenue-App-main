from flask import jsonify

from application import application


@application.route('/')
def index():
    return jsonify({'message': 'Hello'})
