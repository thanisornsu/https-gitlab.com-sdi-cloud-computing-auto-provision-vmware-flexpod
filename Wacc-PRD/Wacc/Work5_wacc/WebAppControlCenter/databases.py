import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from app import app
print 'start init db'


db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "create_date": self.create_date
        }


class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    organize = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "customer_id": self.customer_id,
            "username": self.username,
            "password": self.password,
            "organize": self.organize,
            "create_date": self.create_date
        }


class Vm(db.Model):
    __tablename__ = 'vm'
    vm_id = db.Column(db.Integer, primary_key=True)
    vm_name = db.Column(db.String(255), unique=True, nullable=False)
    vm_password = db.Column(db.String(255), nullable=False)
    vm_link = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, nullable=False)
    datastore_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "vm_id": self.vm_id,
            "vm_name": self.vm_name,
            "vm_password": self.vm_password,
            "vm_link": self.vm_link,
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "datastore_id": self.datastore_id,
            "type": self.type,
            "create_date": self.create_date
        }


class Template(db.Model):
    __tablename__ = 'template'
    template_id_count = db.Column(db.Integer, primary_key=True)
    template_name = db.Column(db.String(255), unique=True, nullable=False)
    template_id = db.Column(db.String(255), nullable=False)
    library_id = db.Column(db.String(255), nullable=False)
    vm_id = db.Column(db.Integer, nullable=False)
    cpu = db.Column(db.String(255), nullable=False)
    memory = db.Column(db.String(255), nullable=False)
    disk = db.Column(db.String(255), nullable=False)
    os = db.Column(db.String(255), nullable=False)
    network = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "template_id_count": self.template_id_count,
            "template_name": self.template_name,
            "template_id": self.template_id,
            "library_id": self.library_id,
            "vm_id": self.vm_id,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "os": self.os,
            "network": self.network
        }


class Vmspec(db.Model):
    __tablename__ = 'vm_spec'
    vm_count = db.Column(db.Integer, primary_key=True)
    vm_id = db.Column(db.String(255), nullable=False)
    cpu = db.Column(db.String(255), nullable=False)
    memory = db.Column(db.String(255), nullable=False)
    disk = db.Column(db.String(255), nullable=False)
    os = db.Column(db.String(255), nullable=False)
    network = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "vm_count": self.vm_count,
            "vm_id": self.vm_id,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "os": self.os,
            "network": self.network
        }


class Datastore(db.Model):
    __tablename__ = 'data_store'
    datastore_id = db.Column(db.Integer, primary_key=True)
    datastore_name = db.Column(db.String(255), nullable=False)
    free_space = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Float, nullable=False)

    def response(self):
        return {
            "datastore_id": self.datastore_id,
            "datastore_name": self.datastore_name,
            "free_space": self.free_space,
            "capacity": self.capacity
        }


class Network(db.Model):
    __tablename__ = 'network'
    network_ip = db.Column(db.String(50), primary_key=True)
    network_type = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.String(255), nullable=False)

    def response(self):
        return {
            "network_ip": self.network_ip,
            "network_type": self.network_type,
            "create_data": self.create_date
        }


# class WorkChannel(db.Model):
#     __tablename__ = 'workchannels'
#     id = db.Column(db.Integer, db.Sequence('seq_workch_id',
#                                            start=1, increment=1), primary_key=True)
#     name = db.Column(db.String, unique=True, nullable=False)

#     def __init__(self, name):
#         self.name = name

#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#         }


# class Platform(db.Model):
#     __tablename__ = 'platforms'
#     id = db.Column(db.Integer, db.Sequence('seq_platform_id',
#                                            start=1, increment=1), primary_key=True)
#     name = db.Column(db.String, unique=True, nullable=False)

#     def __init__(self, name):
#         self.name = name

#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#        }


# class Group(db.Model):
#     __tablename__ = 'groups'
#     id = db.Column(db.Integer, db.Sequence('seq_groups_id',
#                                            start=1, increment=1), primary_key=True)
#     name = db.Column(db.String, unique=True, nullable=False)
#
#     def __init__(self, name):
#         self.name = name
#
#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#         }
#
#
# class Incident(db.Model):
#     __tablename__ = 'incidents'
#     id = db.Column(db.Integer, primary_key=True)
#     task = db.Column(db.String(150), nullable=False)
#     url = db.Column(db.String)
#     team_owner = db.Column(db.String(100), nullable=False)
#     work_channel = db.Column(db.String(100), nullable=False)
#     staff = db.Column(db.Integer, db.ForeignKey('staffs.id'), nullable=False)
#     priority = db.Column(db.Integer)
#     risk = db.Column(db.String, default='Green')
#     status = db.Column(db.String, nullable=False)
#     start_date = db.Column(db.Integer, default=int(time.time()))
#     end_date = db.Column(db.Integer)
#     description = db.Column(db.String)
#     group = db.Column(db.String)
#     release_date = db.Column(db.Integer)
#     staffs = db.relationship('Staff')
#
#     def __init__(self, task, team_owner, work_channel, staff, status, url=None, priority=1, risk=1,
#                  start_date=None, end_date=None, description=None, group=None, release_date=None):
#         self.task = task
#         self.team_owner = team_owner
#         self.work_channel = work_channel
#         self.staff = staff
#         self.status = status
#         self.risk = risk
#         self.url = url
#         self.priority = priority
#         self.start_date = start_date
#         self.end_date = end_date
#         self.description = description
#         self.group = group
#         self.release_date = release_date
#
#     def response(self):
#         data = {
#             "id": str(self.id),
#             "task": self.task,
#             "url": self.url,
#             "team_owner": self.team_owner,
#             "work_channel": self.work_channel,
#             "staff": self.staffs.name_en,
#             "priority": self.priority,
#             "risk": self.risk,
#             "status": self.status,
#             "start_date": self.start_date,
#             "end_date": self.end_date,
#             "description": self.description,
#             "group": self.group,
#             "release_date": self.release_date
#         }
#         return data


# class Table1(db.Model):
#     __tablename__ = 'model1'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))

#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#         }

# class Table2(db.Model):
#     __tablename__ = 'model2'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#         }
#
# class Table3(db.Model):
#     __tablename__ = 'model3'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     def as_dict(self):
#         return {
#             'id': self.id,
#             'name': str(self.name),
#         }


def init_db():
    # db.engine.execute("drop database let_do_it cascade;")
    # db.engine.execute("create database let_do_it;")
    # db.engine.execute("drop table incidents;")
    db.create_all()

    # print User.response()
print 'finish init db'
