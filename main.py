import asyncio
from includes.config import *
from utils.setup_rpc import create_nodes_dict, swap_signer_backup

# 1.  Check that they are doing what they are supposed to do.. Check Flag and if required turn on for Signer and Flag off for Backup
# 2.  Cross reference viewId and make sure they are in sync.  If not throw an Error and send alert.
# 2a. A threshold should be set (X blocks out of sync) to switch signing if the sync is too far out.
# 3.  If no response is found, turn on the backup flag and switch the nodes around in the dict.
# 4. Check any other monitor nodes are alive! add simple uvicorn api and save an update every minute that can be checked by the other node.
# 5. Repeat.


async def check(nodes_to_monitor: dict):
    for k, v in nodes_to_monitor.items():
        log.info(f"Checking {k.title()}")
        for node_type, rpc in v.items():
            log.info(f"Node Type = {node_type} | IP: {rpc.node}")
            log.info(f"{node_type} Flag Status: {await rpc.get_flag_status()}")
            if node_type == "Signer":
                log.info(
                    f'Turning Signer Flag OFF: {await rpc.toggle_flag(toggle=False, fn="toggle")}'
                )
                log.info(f"Signer Flag Status: {await rpc.get_flag_status()}")
            else:
                log.info(
                    f'Turning Backup Flag ON: {await rpc.toggle_flag(toggle=False, fn="toggle")}'
                )
                log.info(f"Backup Flag Status: {await rpc.get_flag_status()}")

        swapped = swap_signer_backup(v)
        nodes_to_monitor[k].update(swapped)

    for node_type, rpc in v.items():
        log.info(f"New Node Type: {node_type} Node IP: {rpc.node}")
        await check_external(rpc)


async def close_all_sessions(nodes_to_monitor: dict):
    for k, v in nodes_to_monitor.items():
        log.info(f"Ending Nodes Sessions for [ {k.title()} ]")
        for node_type, rpc in v.items():
            log.info(f"Ending Session for {node_type} Node |  {rpc.node}")
            await rpc.close_session()


async def main():
    nodes_to_monitor = create_nodes_dict(nodes)
    i = 1
    while 1:
        log.info(f"Running Async Number {i}")
        await check(nodes_to_monitor)
        i += 1
    await close_all_sessions(nodes_to_monitor)


async def check_external(rpc):
    # check_flag("https://harmony-0-rpc.gateway.pokt.network")
    view_id, epoch, block_number = await rpc.get_external_data()
    log.info(f" ViewID External        ::  {view_id}")
    log.info(f" Epoch External         ::  {epoch}")
    log.info(f" Block Number External  ::  {block_number}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
