# -*- coding: utf-8 -*
import Provisioning
from flask import Blueprint


# ============== Flask router register ==============

routes = Blueprint('/provisioning', __name__)
routes.add_url_rule(
    'vmname/<vm_name>',
    'vmname',
    Provisioning.vmName,
    methods=['GET'],
)

routes.add_url_rule(
    'storage',
    'storage',
    Provisioning.getStorage,
    methods=['GET'],
)

routes.add_url_rule(
    'templates',
    'templates',
    Provisioning.getTemplates,
    methods=['GET'],
)

routes.add_url_rule(
    'templates/<template_id>',
    'templateByID',
    Provisioning.getTemplateId,
    methods=['GET'],
)

routes.add_url_rule(
    'networks',
    'networks',
    Provisioning.getNetworks,
    methods=['GET'],
)

routes.add_url_rule(
    '',
    'deploy',
    Provisioning.deployMachine,
    methods=['POST'],
)

routes.add_url_rule(
    'specification',
    'deploy/specification',
    Provisioning.deploySpecialMachine,
    methods=['POST'],
)

routes.add_url_rule(
    'table/<table_name>',
    'table',
    Provisioning.getDatabaseData,
    methods=['POST'],
)