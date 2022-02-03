from utils.call_rpc import RPC


def create_nodes_dict(node_pairs: dict) -> RPC:
    d = {}
    c = 1
    for node1_ip, node2_ip in node_pairs.items():
        rpc1 = RPC(node1_ip)
        rpc1.update_node_metadata()
        rpc2 = RPC(node2_ip)
        rpc2.update_node_metadata()

        d.update({f"node_pair_{c}": {"Signer": rpc1, "Backup": rpc2}})
        c += 1
    return d


def swap_signer_backup(d: dict) -> dict:
    return {"Signer": d["Backup"], "Backup": d["Signer"]}


rpc_external = RPC("None")
