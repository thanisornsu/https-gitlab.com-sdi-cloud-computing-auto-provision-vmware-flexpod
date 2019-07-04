# -*- coding: utf-8 -*
import controller
from flask import Blueprint


# ============== Flask router register ==============

routes = Blueprint('/users', __name__)
routes.add_url_rule(
    '',
    'getUserData',
    controller.getUserData,
    methods=['GET'],
)

routes.add_url_rule(
    '',
    'createUser',
    controller.createUser,
    methods=['POST'],
)

