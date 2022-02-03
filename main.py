from includes.config import *
from utils.setup_rpc import create_nodes_dict, swap_signer_backup, rpc_external

nodes_to_monitor = create_nodes_dict(nodes)
for k, v in nodes_to_monitor.items():
    log.info(f"Checking {k.title()}")
    for node_type, rpc in v.items():
        log.info(f"Node Type = {node_type} Node IP: {rpc.node}")
        log.info(f"Flag Status: {rpc.get_flag_status()}")
        if node_type == "Signer":
            log.info(
                f'Turning Signer Flag OFF: {rpc.toggle_flag(toggle=False, fn="toggle")}'
            )
            rpc.update_node_metadata()
            log.info(f"Signer Flag Status: {rpc.get_flag_status()}")
        else:
            log.info(
                f'Turning Backup Flag ON: {rpc.toggle_flag(toggle=False, fn="toggle")}'
            )
            rpc.update_node_metadata()
            log.info(f"Backup Flag Status: {rpc.get_flag_status()}")

    swapped = swap_signer_backup(v)
    nodes_to_monitor[k].update(swapped)

    for node_type, rpc in v.items():
        log.info(f"New Node Type: {node_type} Node IP: {rpc.node}")

print(nodes_to_monitor)

# rpc.get_flag_status()
# rpc.toggle_flag(toggle=False, fn='toggle')

# check_flag("https://harmony-0-rpc.gateway.pokt.network")
latest = rpc_external.update_latest_headers()
view_id, epoch, block_number = rpc_external.get_external_data()
log.info(f" ViewID External        ::  {view_id}")
log.info(f" Epoch External         ::  {epoch}")
log.info(f" Block Number External  ::  {block_number}")
