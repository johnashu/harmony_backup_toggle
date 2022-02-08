import asyncio
from platform import node

from includes.config import *
from utils.setup_rpc import create_nodes_dict, swap_signer_backup, RPC

# 1.  Check that they are doing what they are supposed to do.. Check Flag and if required turn on for Signer and Flag off for Backup
async def check_and_update_flag(node_type: str, rpc: RPC) -> bool:
    switch = states[node_type]
    log.info(f"Node Type = {node_type} | Name:  {rpc.name}  |  IP: {rpc.node}")
    flag_res, flag_state = await rpc.get_flag_status()
    if flag_res:
        log.info(f"{node_type} Current Flag Status: {flag_state}")
        if flag_state == switch:
            return True
        log.info(f"Turning {node_type} Flag {'ON' if switch else 'OFF' }..")
        toggle_res, _ = await rpc.toggle_flag(toggle=switch, fn="toggle")
        if toggle_res:
            flag_res, flag_state = await rpc.get_flag_status()
            log.info(f"{node_type} Flag Status: {flag_state}")
            return flag_state == switch
    return False


# 1a.  Check mode == Normal for signing and NormalBackup for backup - Can be syncing and handled with the blocks misaligned


# 2.  Cross reference viewId and make sure they are in sync.  If not throw an Error and send alert.
# 2a. A threshold should be set (X blocks out of sync) to switch signing if the sync is too far out.


async def check_view_id_sync(rpc: RPC) -> bool:
    """Display Harmony External Node data from a Local Node Session

    Args:
        rpc (RPC): ClientSession object of the node.
    """
    res, view_id, epoch, block_number = await rpc.get_external_epoch_data()
    ires, iview_id, iepoch, iblock_number = await rpc.get_internal_epoch_data()
    if ires and res:
        log.info(
            f"\nViewID External        ::  {view_id}\nViewID Internal        ::  {iview_id}"
        )
        log.info(
            f"\nEpoch External         ::  {epoch}\nEpoch Internal         ::  {iepoch}"
        )
        log.info(
            f"\nBlock Number External  ::  {block_number}\nBlock Number Internal  ::  {iblock_number}"
        )
        view_id_diff = int(iview_id) - int(view_id)
        if view_id_diff >= OUT_OF_SYNC_THRES:
            err = f"ViewId out of sync : {view_id_diff}"
            rpc.errors.append(err)
            return False
        return True
    return False


# 3.  If no response is found, turn on the backup flag and switch the nodes around in the dict.


async def swap_roles(i: int, v: dict, nodes_to_monitor: dict) -> dict:
    swapped = swap_signer_backup(v)
    nodes_to_monitor[i] = swapped
    for node_type, rpc in v.items():
        log.info(f"New Node Type: {node_type} | Name:  {rpc.name}  |  IP: {rpc.node}")
    return nodes_to_monitor


# 4. Check any other monitor nodes are alive! add simple uvicorn api and save an update every minute that can be checked by the other node.
async def check_other_monitors_alive(monitor_services: tuple) -> bool:
    for x in monitor_services:
        log.info(x)
    return True


# 5. Sleep Eat Repeat.
async def chillax() -> None:
    log.info(f"All Nodes checked, sleeping for {DELAY_BETWEEN_CHECKS} seconds")
    await asyncio.sleep(DELAY_BETWEEN_CHECKS)


async def check(nodes_to_monitor: dict) -> dict:
    for i, x in enumerate(nodes_to_monitor):
        swap = False
        log.info(f"Checking Node Pair {i+1}")
        for node_type, rpc in x.items():
            in_correct_state = await check_and_update_flag(node_type, rpc)
            if not in_correct_state:
                swap = True
                log.error(rpc.errors)
            view_id_synced = await check_view_id_sync(rpc)
            if not view_id_synced:
                swap = True
                log.error(rpc.errors)
        if swap:
            nodes_to_monitor = await swap_roles(i, x, nodes_to_monitor)
    return nodes_to_monitor


async def close_all_sessions(nodes_to_monitor: dict) -> None:
    """Close all sessions that are open for a greaceful shutdown and to avoid Asynce logging error

    Args:
        nodes_to_monitor (dict): Nodes and objects of sessions to close.
    """
    for i, x in enumerate(nodes_to_monitor):
        log.info(f"Ending Nodes Sessions for  Node Pair {i+1}")
        for node_type, rpc in x.items():
            log.info(f"Ending Session for {node_type} Node |  {rpc.node}")
            await rpc.close_session()


async def main():
    nodes_to_monitor = create_nodes_dict(nodes)
    i = 1
    while 1:
        try:
            log.info(f"Running Async Number {i}")
            nodes_to_monitor = await check(nodes_to_monitor)
            await check_other_monitors_alive(monitor_services)
            await chillax()
        except Exception as e:
            log.error(f"A general Erorr occurred in the main loop : {e}")
    await close_all_sessions(nodes_to_monitor)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
