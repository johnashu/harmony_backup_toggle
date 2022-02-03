import logging, sys, json, os
from utils.helpers import create_data_path
from includes.parse_envs import Envs

envs = Envs()
for x in envs.nodes:
    print(x)
create_data_path("", data_path='logs')
create_data_path("", data_path='data')

port = 9500
# pair up nodes that complement each other.. if 1 goes down, the other will come up.
nodes = {
f"http://154.53.50.54:{port}": f"http://66.94.122.253:{port}"  # west
}

# LOGGING
file_handler = logging.FileHandler(filename=os.path.join("logs", "data.log"))
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
    handlers=handlers,
    datefmt="%d-%m-%Y %H:%M:%S",
)

log = logging.getLogger()
