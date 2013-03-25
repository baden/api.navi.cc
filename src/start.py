import os
from logging.config import dictConfig as initLogging

from configs import Config

environment = os.environ.get("APPLICATION_ENV", 'production') #TODO add argv support
config = Config.load("application.yaml", environment, "application-personal.yaml")
initLogging(config.get("logging"))

from application import Application

app = Application(environment, config)
app.bootstrap()
if __name__ == "__main__":
    app.run()

