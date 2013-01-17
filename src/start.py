import os

from configs import Config
from logging.config import dictConfig as initLogging

environment = os.environ.get("APPLICATION_ENV", 'production') #TODO add argv support
config = Config.load(environment)
initLogging(config.get("logging"))


from application import Application
app = Application(environment, config)
app.bootstrap()
app.run()

