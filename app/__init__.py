import logging

from flask import app

from flask_appbuilder import AppBuilder, SQLA

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)


#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)ß
