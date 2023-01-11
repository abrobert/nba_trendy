import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)ß

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
db.init_app(app)

#appbuilder = AppBuilder(app, db.session)
appbuilder = AppBuilder(app, db.session, base_template='custom_base.html')

"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""

from . import views

db.create_all()
appbuilder.add_view(
    views.PlayModelView, "List Plays", icon="fa-envelope", category="Plays"
)
appbuilder.add_view(
    views.CustomPlayModelView, "List Custom Plays", icon="fa-envelope", category="Plays"
)
#appbuilder.add_view(CustomPlayModelView, "List Custom Plays", href=CustomPlayModelView.endpoint+"/table/", icon="fa-envelope", category="Plays")
appbuilder.add_view(
    views.PlayChartView,
    "Show Play Chart",
    icon="fa-dashboard",
    category="Statistics",
)
appbuilder.add_view(
    views.PlayChartView2,
    "Show Play Chart2",
    icon="fa-dashboard",
    category="Statistics",
)
appbuilder.add_view(views.MyView, "Method1", category='My View')
appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')
appbuilder.add_link("Method3", href='/myview/method3/john', category='My View')
