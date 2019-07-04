import sqlalchemy as db
import pymysql
pymysql.install_as_MySQLdb()

username = "sdiadmin"
password = "epMRuvkZPMsx2X4E"

set_path = db.create_engine('mysql+pymysql://sdiadmin:epMRuvkZPMsx2X4E@10.10.21.51:3306/lup_test_sql')
connection = set_path.connect()
metadata = db.MetaData()
user_column = db.Table('user', metadata, autoload=True, autoload_with=set_path)

print(user_column.columns.keys())

query = db.select([user_column])
ResultProxy = connection.execute(query)
ResultSet = ResultProxy.fetchall()
print ResultSet
