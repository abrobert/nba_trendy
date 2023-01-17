import logging

from flask import   Flask
from app import app as curr_app
from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

with app.app_context():
    
    app.config.from_object("config")
    
    db = SQLA(app)

    db.init_app(app)

    appbuilder = AppBuilder(app, db.session, base_template='custom_base.html')
    db.create_all()

    from .views import PlayModelView, CustomPlayModelView

    appbuilder.add_view(
        PlayModelView, "List Plays", icon="fa-envelope", category="Plays"
    )
    appbuilder.add_view(
        CustomPlayModelView, "List Custom Plays", icon="fa-envelope", category="Plays"
    )
  
