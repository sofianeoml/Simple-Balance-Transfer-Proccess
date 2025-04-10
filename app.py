from flask import Flask
from routes.routes import init_routes

app = Flask(__name__, template_folder='pages', static_folder='static')
app.secret_key = '1XSEC'

@app.template_filter('timestamp_to_date')
def timestamp_to_date(ms):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

import dbs.users
import dbs.transactions
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)