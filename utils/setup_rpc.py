from utils.call_rpc import RPC, aiohttp


def create_nodes_dict(node_pairs: dict) -> RPC:
    d = {}
    c = 1
    for node1_ip, node2_ip in node_pairs.items():
        rpc1 = RPC(node1_ip, aiohttp.ClientSession)
        rpc2 = RPC(node2_ip, aiohttp.ClientSession)
        d.update({f"node_pair_{c}": {"Signer": rpc1, "Backup": rpc2}})
        c += 1
    return d


def swap_signer_backup(d: dict) -> dict:
    return {"Signer": d["Backup"], "Backup": d["Signer"]}
