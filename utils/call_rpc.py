import aiohttp
from includes.config import *
from typing import Tuple


class RPC:
    def __init__(self, node: str, name: str) -> None:
        self.session = aiohttp.ClientSession()
        self.node = node
        self.name = name
        self.shard = 0
        self.local_metadata = {}
        self.external_headers = {}
        self.messages = []

    async def close_session(self) -> None:
        """Close Async Session"""
        await self.session.close()

    def save_data(self, fn: str, data: dict) -> None:
        """Save response data to json file.

        Args:
            fn (str): Filename to save
            data (dict): dict to save to Json
        """
        fn = fn.split("//")[-1].split(":")[0].replace(".", "_")
        with open(os.path.join("data", f"{fn}.json"), "w") as j:
            json.dump(data, j, indent=4)

    async def call_rpc_single_page(
        self,
        method: str,
        rpc_endpoint: str,
        params: list = [],
        _id: int = 1,
        fn: str = "data",
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

        res = False
        headers = {"Content-Type": "application/json"}

        d = {"jsonrpc": "2.0", "method": method, "params": params, "id": str(_id)}
        try:
            async with self.session.post(
                rpc_endpoint, json=d, headers=headers, verify_ssl=False
            ) as resp:
                data = await resp.json()
                data = data["result"]
                res = True
        except (json.decoder.JSONDecodeError, KeyError, TypeError) as e:
            data = {"error": f"Json Error:  {await resp.text()}"}
            log.error(e)
            self.messages.append(data)
        except (aiohttp.ClientConnectorError, aiohttp.ClientOSError) as e:
            log.error(e)
            data = {"error": f"Cannot Connect:  {e}"}
            self.messages.append(data)
        self.save_data(f"{rpc_endpoint}-{fn}", data)
        return res, data

    async def toggle_flag(self, toggle: bool = True, **kw) -> Tuple[bool, bool]:
        """Turn Flag on (True) / off (False)

        Args:
            node (str): ip / port address of the node to talk to.
            toggle (bool, optional): Turn Flag on (True) / off (False). Defaults to True (ON).

        Returns:
            bool: confirmation flag was successful.
        """
        res, toggle = await self.call_rpc_single_page(
            "hmy_setNodeToBackupMode", self.node, [toggle], _id=1, **kw
        )
        return res, toggle

    async def get_external_epoch_data(self) -> Tuple[bool, int, int, int]:
        updated = await self._update_latest_headers()
        if updated:
            return (
                True,
                self.external_headers.get("viewID"),
                self.external_headers.get("epoch"),
                self.external_headers.get("blockNumber"),
            )
        return False, 0, 0, 0

    async def get_internal_epoch_data(self) -> Tuple[bool, int, int, int]:
        updated = await self._update_node_metadata()
        if updated:
            return (
                True,
                self.local_metadata.get("consensus", {"viewId": 0}).get("viewId"),
                self.local_metadata.get("current-epoch"),
                self.local_metadata.get("current-block-number"),
            )
        return False, 0, 0, 0

    async def get_flag_status(self) -> Tuple[bool, bool]:
        """Check the status of the backup flag for the node passed.

        Returns:
            tuple: check_result, Status of the flag ON (True) / OFF (False)
        """
        updated = await self._update_node_metadata()
        if updated:
            return True, self.local_metadata.get("is-backup")
        return False, False

    async def _update_latest_headers(self) -> bool:
        """Updates the latest data from Harmony External Node for the Shard passed."""
        res, header = await self.call_rpc_single_page(
            "hmyv2_latestHeader",
            f"https://api.s{self.shard}.t.hmny.io",
            [],
            _id=1,
            fn="external-header",
        )
        if res:
            self.external_headers = header
            return True
        return False

    async def _update_node_metadata(self) -> bool:
        """Updates the latest metadata from Harmony Local Node."""
        res, metadata = await self.call_rpc_single_page(
            "hmyv2_getNodeMetadata", self.node, [], _id=1
        )
        if res:
            self.local_metadata = metadata
            self.shard = metadata["shard-id"]
            return True
        return False
