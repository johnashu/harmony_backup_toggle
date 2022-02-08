import logging, sys, json, os
import socket
from includes.config_utils import Envs, hot_reload_data, create_data_path

envs = Envs()
create_data_path("", data_path="logs")
create_data_path("", data_path="data")

states = dict(Signer=False, Backup=True)

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

hostname = socket.gethostname()
log.info(hostname)
externalIP = os.popen("curl -s ifconfig.me").readline()
log.info(externalIP)
