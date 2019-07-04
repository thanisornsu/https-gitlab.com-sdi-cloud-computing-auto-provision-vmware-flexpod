import mainBackend
from flask import Blueprint

# ============== Flask router register ==============

vm_routes = Blueprint('/vm', __name__)
vm_routes.add_url_rule(
    '',
    'vm_name',
    mainBackend.getData,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/storage',
    'vm_storage',
    mainBackend.getStorage,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org',
    'get_org',
    mainBackend.getOrg,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org/<string:org_name>',
    'get_vdc',
    mainBackend.getVdc,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org/<string:org_name>/<string:vdc_name>',
    'get_vapp',
    mainBackend.getVapp,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '',
    'provisioning',
    mainBackend.startThread,
    methods=['POST'],
)

vm_routes.add_url_rule(
    '/status',
    'status_checking',
    mainBackend.statusTask,
    methods=['GET'],
)

volume_routes = Blueprint('/storage', __name__)
volume_routes.add_url_rule(
    '',
    'volume',
    mainBackend.returnVolume,
    methods=["POST"]
)

volume_routes.add_url_rule(
    '/aggregate',
    'aggregate',
    mainBackend.getAggregate,
    methods=["GET"]
)

volume_routes.add_url_rule(
    '/vserver',
    'vserver',
    mainBackend.checkVServer,
    methods=["GET"]
)

volume_routes.add_url_rule(
    '/offline',
    'offline_volumes',
    mainBackend.offline,
    methods=["PUT"]
)

volume_routes.add_url_rule(
    '',
    'delete_volumes',
    mainBackend.returnDelete,
    methods=["DELETE"]
)

volume_routes.add_url_rule(
    '',
    'volumes',
    mainBackend.checkVolume,
    methods=["GET"]
)

network_routes = Blueprint('/network', __name__)
network_routes.add_url_rule(
    '',
    'create_edge_gateway',
    mainBackend.createNSX,
    methods=["POST"]
)

network_routes.add_url_rule(
    '/vlan',
    'create_vlan',
    mainBackend.createVlan,
    methods=["POST"]
)

compute_routes = Blueprint('/compute', __name__)
compute_routes.add_url_rule(
    '',
    'compare_blade',
    mainBackend.comparisonBlade,
    methods=['GET'],
)

