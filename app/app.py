import logging

from flask import current_app, Flask

from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

def create_app() -> Flask:
    app = Flask(__name__)

    try:
        logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
        logging.getLogger().setLevel(logging.DEBUG)


        #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)ß
        with app.app_context():
        # app = Flask(__name__)
            
            app.config.from_object("config")
            db = SQLA(app)
            #from views import CustomPlayModelView, PlayModelView, PlayChartView, PlayChartView2, MyView

            db.init_app(app)

            #appbuilder = AppBuilder(app, db.session)
            appbuilder = AppBuilder(app, db.session, base_template='custom_base.html')
            db.create_all()

            from views import PlayModelView

            #from views import CustomPlayModelView, PlayModelView, PlayChartView, PlayChartView2, MyView
            appbuilder.add_view(
                PlayModelView, "List Plays", icon="fa-envelope", category="Plays"
            )
            # appbuilder.add_view(
            #     CustomPlayModelView, "List Custom Plays", icon="fa-envelope", category="Plays"
            # )
            # #appbuilder.add_view(CustomPlayModelView, "List Custom Plays", href=CustomPlayModelView.endpoint+"/table/", icon="fa-envelope", category="Plays")
            # appbuilder.add_view(
            #     PlayChartView,
            #     "Show Play Chart",
            #     icon="fa-dashboard",
            #     category="Statistics",
            # )
            # appbuilder.add_view(
            #     PlayChartView2,
            #     "Show Play Chart2",
            #     icon="fa-dashboard",
            #     category="Statistics",
            # )
            # appbuilder.add_view(MyView, "Method1", category='My View')
            # appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')
            # appbuilder.add_link("Method3", href='/myview/method3/john', category='My View')

        return app
    except Exception as ex:
        raise ex

