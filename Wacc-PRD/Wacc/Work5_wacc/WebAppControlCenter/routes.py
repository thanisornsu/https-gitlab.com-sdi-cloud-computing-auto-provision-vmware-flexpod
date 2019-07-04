print 'start init routing'
# from .incident.routing import routes as incident_route
# from .department.routing import routes as department_route
# from .staff.routing import routes as staff_route
# from .authener.routing import routes as authener_route
from .provisioning.routing import routes as provisioning_route
from .user.routing import routes as user_route
# from .controller.routing import routes as backend_route
# from .controller.routing import storage_routes as storage_route
from .controller.mainRouting import vm_routes as backend_route
from .controller.mainRouting import volume_routes as volume_route
from .controller.mainRouting import network_routes as network_route
from .controller.mainRouting import compute_routes as compute_routes
from .app import app


def root_endpoint():
    return 'Hello World.'


def init_routes():
    app.add_url_rule( '/',
                      'root_endpoint',
                      root_endpoint,
                      methods=['GET'],
                    )
    # app.register_blueprint(authener_route, url_prefix="/api/v1")
    # app.register_blueprint(incident_route,url_prefix="/api/v1/scripts")
    # app.register_blueprint(staff_route, url_prefix="/api/v1/staffs")
    app.register_blueprint(user_route,url_prefix="/api/v1/users")
    # app.register_blueprint(department_route, url_prefix="/api/v1/departments")
#    app.register_blueprint(department_route, url_prefix="/api/v1/platform")
#     app.register_blueprint(provisioning_route, url_prefix="/api/v1/vm")
    app.register_blueprint(backend_route, url_prefix="/api/v1/vm")
    app.register_blueprint(volume_route, url_prefix="/api/v1/volume")
    app.register_blueprint(network_route, url_prefix="/api/v1/network")
    app.register_blueprint(compute_routes, url_prefix="/api/v1/compute")


print 'finish init routing'

