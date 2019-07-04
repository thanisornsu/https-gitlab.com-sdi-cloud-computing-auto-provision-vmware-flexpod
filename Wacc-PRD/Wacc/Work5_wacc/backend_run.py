from WebAppControlCenter.app import app
from WebAppControlCenter.databases import init_db
from WebAppControlCenter.routes import init_routes


# sess = db.session
init_db()
init_routes()
#for user in sess.query(User):
#    print user.response()

app.run(host="127.0.0.1", port=5001)

