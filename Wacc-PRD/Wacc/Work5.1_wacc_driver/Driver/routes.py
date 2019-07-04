from .app import app
from .mainDriver.routing import vm_routes as vm_route
from .mainDriver.routing import volume_routes as volume_routes
from .mainDriver.routing import network_routes as network_routes
from .mainDriver.routing import compute_routes as compute_routes


def root_endpoint():
    return 'Hello.'


def init_routes():
    app.add_url_rule( '/',
                      'root_endpoint',
                      root_endpoint,
                      methods=['GET'],
                    )
    # app.register_blueprint(authener_route, url_prefix="/api/v1")
    # app.register_blueprint(incident_route,url_prefix="/api/v1/scripts")
    # app.register_blueprint(staff_route, url_prefix="/api/v1/staffs")
    # app.register_blueprint(department_route, url_prefix="/api/v1/departments")
#    app.register_blueprint(department_route, url_prefix="/api/v1/platform")
#     app.register_blueprint(provisioning_route, url_prefix="/api/v1/vm")
#     app.register_blueprint(user_route,url_prefix="/api/v1/users")
#     app.register_blueprint(storage_route, url_prefix="/api/v1/storage")
    app.register_blueprint(vm_route, url_prefix="/api/v1/vm")
    app.register_blueprint(volume_routes, url_prefix="/api/v1/volume")
    app.register_blueprint(network_routes, url_prefix="/api/v1/network")
    app.register_blueprint(compute_routes, url_prefix="/api/v1/compute")

