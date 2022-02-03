from requests import post
from includes.config import *


def call_rpc_single_page(
    method: str,
    rpc_endpoint: str,
    params: list = [],
    _id: int = 1,
    fn: str = 'data'
) -> dict:
    """Base RPC function to call data..

    Args:
        method (str): method name to call
        rpc_endpoint (str): http RPC endpoint
        params (list, optional): Args to pass to the method. Defaults to [].
        _id (int, optional): id specified for the method. Defaults to 1.
        fn (str, optional): filename to store any data. Defaults to 'data'.

    Returns:
        dict: json reponse of the call.
    """

    headers = {"Content-Type": "application/json"}

    d = {"jsonrpc": "2.0", "method": method, "params": params, "id": str(_id)}

    data = post(rpc_endpoint, json=d, headers=headers)

    try:
        data = data.json()["result"]
        with open(os.path.join("data", f"{fn}.json"), "w") as j:
            json.dump(data, j, indent=4)
    except json.decoder.JSONDecodeError:
        data = data.txt
        with open(os.path.join("data", f"{fn}.txt"), "w") as f:
            f.write(data)
    return data


def check_flag(node: str, **kw) -> bool:
    """Check the status of the backup flag ror the node passed.

    Args:
        node (str): http address of the node to check.

    Returns:
        bool: Status of the flag ON (True) / OFF (False)
    """
    try:
        check = call_rpc_single_page(
            "hmy_getNodeMetadata",
            node,
            [],
            _id=1,
            **kw
        )["is-backup"]
        log.info(check)
        return check
    except Exception as e:
        log.info(e)


def toggle_flag(node: str, toggle: bool = True, **kw) -> bool:
    """Turn Flag on (True) / off (False)

    Args:
        node (str): ip / port address of the node to talk to.
        toggle (bool, optional): Turn Flag on (True) / off (False). Defaults to True (ON).

    Returns:
        bool: confirmation flag was successful.
    """
    try:
        toggle = call_rpc_single_page(
            "hmy_setNodeToBackupMode",
            node,
            [toggle],
            _id=1,
            **kw
        )
        log.info(toggle)
        check = check_flag(node)
        log.info(check)
        return check
    except Exception as e:
        log.info(e)
