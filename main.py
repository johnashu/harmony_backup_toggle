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
        log.info(f"View ID Difference between nodes = {view_id_diff}")
        if view_id_diff <= -envs.OUT_OF_SYNC_THRES:
            err = {"error": f"ViewId out of sync : {view_id_diff}"}
            rpc.messages.append(err)
            return False
        return True
    return False


# 3.  If no response is found, turn on the backup flag and switch the nodes around in the dict.
async def swap_roles(i: int, v: dict, nodes_to_monitor: dict) -> dict:
    swapped = swap_signer_backup(v)
    nodes_to_monitor[i] = swapped
    for node_type, rpc in v.items():
        swapped_msg = {
            "swapped": f"New Node Type: {node_type} | Name:  {rpc.name}  |  IP: {rpc.node}"
        }
        log.info(swapped_msg["swapped"])
        rpc.messages.append(swapped_msg)
    return nodes_to_monitor


# 4. Check any other monitor nodes are alive! add simple uvicorn api and save an update every minute that can be checked by the other node.
async def check_other_monitors_alive(monitor_services: tuple) -> bool:
    for x in monitor_services:
        log.info(x)
    return True


# 5. Sleep Eat Repeat.
async def chillax() -> None:
    log.info(f"All Nodes checked, sleeping for {envs.DELAY_BETWEEN_CHECKS} seconds")
    await asyncio.sleep(envs.DELAY_BETWEEN_CHECKS)


async def send_email_alerts(rpc: RPC) -> None:
    from utils._email import send_email

    subject = f"Backup Monitor Alerts - {rpc.name.title()}"
    msg = f"The following actions have occured for [ {rpc.name} ] at address: [ {rpc.node} ]\n\n"
    for x in rpc.messages:
        for k, v in x.items():
            msg += f"{k.title()}: {v}\n\n"
    await send_email(subject, msg)


async def send_alerts(nodes_to_monitor: list) -> None:
    for i, x in enumerate(nodes_to_monitor):
        for _, rpc in x.items():
            if rpc.messages:
                log.info(f"Sending Alerts for Node Pair {i+1}..")
                log.debug(rpc.messages)
                email_sent = await send_email_alerts(rpc)
                if email_sent:
                    rpc.messages = []
                    log.info(rpc.messages)


async def check(nodes_to_monitor: list) -> dict:
    for i, x in enumerate(nodes_to_monitor):
        swap = False
        log.info(f"Checking Node Pair {i+1}")
        for node_type, rpc in x.items():
            in_correct_state = await check_and_update_flag(node_type, rpc)
            if not in_correct_state:
                swap = True
                log.error(rpc.messages)
            view_id_synced = await check_view_id_sync(rpc)
            if not view_id_synced:
                swap = True
                log.error(rpc.messages)
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
            log.info(
                f"Ending Session for  {node_type} | Name:  {rpc.name} IP: {rpc.node}"
            )
            await rpc.close_session()


async def main() -> None:
    i = 1
    while 1:
        try:
            nodes, monitor_services = hot_reload_data(envs)
            nodes_to_monitor = create_nodes_dict(nodes)
            log.info(f"Running Async Number {i}")
            nodes_to_monitor = await check(nodes_to_monitor)
            await check_other_monitors_alive(monitor_services)
            await send_alerts(nodes_to_monitor)
            await chillax()
            await close_all_sessions(nodes_to_monitor)
        except Exception as e:
            log.error(f"A general Erorr occurred in the main loop : {e}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
