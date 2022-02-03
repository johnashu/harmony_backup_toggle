from utils.call_rpc import *


for node1_ip, node2_ip in nodes.items():
    check_flag(node2_ip)
    toggle_flag(node2_ip, toggle=False, fn='toggle')