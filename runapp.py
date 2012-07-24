import os

from paste.deploy import loadapp
from pyramid.paster import setup_logging
from waitress import serve

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    setup_logging('production.ini')
    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)
