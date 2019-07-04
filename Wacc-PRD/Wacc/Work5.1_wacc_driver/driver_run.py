from Driver.app import app
from Driver.routes import init_routes


init_routes()

app.run(host="127.0.0.1", port=5002)

