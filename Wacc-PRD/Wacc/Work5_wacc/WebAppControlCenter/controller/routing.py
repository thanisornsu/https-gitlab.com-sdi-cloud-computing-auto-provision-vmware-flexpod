# -*- coding: utf-8 -*
import backendFunc
from flask import Blueprint


# ============== Flask router register ==============

routes = Blueprint('/controller', __name__)
routes.add_url_rule(
    '',
    'provisioning',
    backendFunc.provisioning,
    methods=['POST'],
)

routes.add_url_rule(
    '',
    'getDetail',
    backendFunc.getData,
    methods=['GET'],
)

routes.add_url_rule(
    '/storage',
    'getStorage',
    backendFunc.getStorage,
    methods=['GET'],
)

storage_routes = Blueprint('/storage', __name__)
storage_routes.add_url_rule(
    '',
    'volume',
    backendFunc.returnStorage,
    methods=["POST"]
)

storage_routes.add_url_rule(
    '/aggregate',
    'aggregate',
    backendFunc.getAggregate,
    methods=["GET"]
)

storage_routes.add_url_rule(
    '/vserver',
    'vserver',
    backendFunc.checkVServer,
    methods=["GET"]
)


storage_routes.add_url_rule(
    '',
    'volumes',
    backendFunc.checkVolume,
    methods=["GET"]
)

storage_routes.add_url_rule(
    '/test',
    'test',
    backendFunc.testFlask,
    methods=["GET"]
)

