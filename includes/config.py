import logging, sys, json, os
from includes.config_utils import Envs, parse_node_list, create_data_path

envs = Envs()
create_data_path("", data_path="logs")
create_data_path("", data_path="data")

port = 9501
# Pair up nodes that compliment each other.  Sames Keys, Different Nodes.
#  if 1 goes down, the other will come up.
nodes = parse_node_list(port=port)

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
