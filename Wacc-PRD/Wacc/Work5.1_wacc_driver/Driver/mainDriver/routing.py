import main
from flask import Blueprint


vm_routes = Blueprint('/controller', __name__)
vm_routes.add_url_rule(
    '',
    'vm_name',
    main.detailData,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org',
    'get_org',
    main.orgData,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org/<string:org_name>',
    'get_vdc',
    main.vdcData,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/org/<string:org_name>/<string:vdc_name>',
    'get_vapp',
    main.vappData,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '/storage',
    'vcenter_storage',
    main.getStorage,
    methods=['GET'],
)

vm_routes.add_url_rule(
    '',
    'provisioning',
    main.sendData,
    methods=['POST'],
)

vm_routes.add_url_rule(
    '/status',
    'status_task',
    main.statusTask,
    methods=['GET'],
)

volume_routes = Blueprint('/volume', __name__)
volume_routes.add_url_rule(
    '',
    'volume',
    main.createMainVolume,
    methods=["POST"]
)

volume_routes.add_url_rule(
    '/aggregate',
    'aggregate',
    main.aggregateValue,
    methods=["GET"]
)

volume_routes.add_url_rule(
    '/vserver',
    'vserver',
    main.vServerName,
    methods=["GET"]
)

volume_routes.add_url_rule(
    '/offline',
    'offline_volumes',
    main.checkStatus,
    methods=["PUT"]
)

volume_routes.add_url_rule(
    '',
    'delete_volume',
    main.volumeDelete,
    methods=["DELETE"]
)

volume_routes.add_url_rule(
    '',
    'volumes',
    main.volumeName,
    methods=["GET"]
)

network_routes = Blueprint('/network', __name__)
network_routes.add_url_rule(
    '/edge',
    'edge',
    main.edge,
    methods=['POST'],
)

network_routes.add_url_rule(
    '/org_vdc_network',
    'org_vdc_network',
    main.vdc_network,
    methods=['POST'],
)

network_routes.add_url_rule(
    '/nat',
    'modify_nat',
    main.nat,
    methods=['POST'],
)

network_routes.add_url_rule(
    '/network_vapp',
    'add_network_vapp',
    main.network_vapp,
    methods=['POST'],
)

network_routes.add_url_rule(
    '/vm_network',
    'vm_connect_network',
    main.vm_network,
    methods=['POST'],
)

network_routes.add_url_rule(
    '',
    'all_connect_network',
    main.nsx_network,
    methods=['POST'],
)

network_routes.add_url_rule(
    '/vlan',
    'all_vlan',
    main.all_vlan,
    methods=['POST'],
)

compute_routes = Blueprint('/compute', __name__)
compute_routes.add_url_rule(
    '',
    'compare_blade',
    main.comparisonBlade,
    methods=['GET'],
)
