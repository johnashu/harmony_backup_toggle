import aiohttp
from includes.config import *
from typing import Union, Tuple


class RPC:
    def __init__(self, node: str, session: aiohttp.ClientSession) -> None:
        self.session = session()
        self.node = node
        self.shard = 0
        self.local_metadata = {}
        self.external_headers = {}

    async def close_session(self) -> None:
        """Close Async Session"""
        await self.session.close()

    def save_data(self, fn: str, data: dict) -> None:
        """Save response data to json file.

        Args:
            fn (str): Filename to save
            data (dict): dict to save to Json
        """
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

        headers = {"Content-Type": "application/json"}

        d = {"jsonrpc": "2.0", "method": method, "params": params, "id": str(_id)}
        async with self.session.post(
            rpc_endpoint, json=d, headers=headers, verify_ssl=False
        ) as resp:
            try:
                data = await resp.json()
                data = data["result"]
            except json.decoder.JSONDecodeError:
                data = {"RAW Data": await resp.text()}
        self.save_data(fn, data)
        return data

    async def toggle_flag(self, toggle: bool = True, **kw) -> bool:
        """Turn Flag on (True) / off (False)

        Args:
            node (str): ip / port address of the node to talk to.
            toggle (bool, optional): Turn Flag on (True) / off (False). Defaults to True (ON).

        Returns:
            bool: confirmation flag was successful.
        """
        try:
            toggle = await self.call_rpc_single_page(
                "hmy_setNodeToBackupMode", self.node, [toggle], _id=1, **kw
            )
            return toggle
        except Exception as e:
            log.error(e)

    async def get_external_data(self) -> Tuple[int, int, int]:
        await self._update_latest_headers()
        return (
            self.external_headers.get("viewID"),
            self.external_headers.get("epoch"),
            self.external_headers.get("blockNumber"),
        )

    async def get_flag_status(self) -> bool:
        """Check the status of the backup flag for the node passed.

        Returns:
            bool: Status of the flag ON (True) / OFF (False)
        """
        await self._update_node_metadata()
        return self.local_metadata.get("is-backup")

    async def _update_latest_headers(self) -> Tuple[int, int, int]:
        """Returns the latest ViewId, epoch and blockNumber from Harmony External Node for the Shard passed.

        Args:
            shard (int): Shard Id to check

        Returns:
            tuple: Current External Nodes ( ViewId , epoch, blocknumber)
        """
        try:
            header = await self.call_rpc_single_page(
                "hmyv2_latestHeader",
                f"https://api.s{self.shard}.t.hmny.io",
                [],
                _id=1,
                fn="external-header",
            )
            self.external_headers = header
        except Exception as e:
            log.error(e)

    async def _update_node_metadata(self, **kw: dict) -> None:
        """Returns the latest metadata from Harmony Local Node.

        Args:
            node (str): http address of the node to check.
        """
        try:
            metadata = await self.call_rpc_single_page(
                "hmyv2_getNodeMetadata", self.node, [], _id=1, **kw
            )
            self.local_metadata = metadata
            self.shard = metadata["shard-id"]
        except Exception as e:
            log.error(e)
