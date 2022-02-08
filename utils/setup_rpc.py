from utils.call_rpc import RPC


def create_nodes_dict(node_pairs: dict) -> list:
    d = []
    for x in node_pairs:
        signing_node_ip = x["Signer"]["ip"]
        backup_node_ip = x["Backup"]["ip"]
        signing_node_name = x["Signer"]["name"]
        backup_node_name = x["Backup"]["name"]
        rpc1 = RPC(signing_node_ip, signing_node_name)
        rpc2 = RPC(backup_node_ip, backup_node_name)
        d.append({"Signer": rpc1, "Backup": rpc2})
    return d


def swap_signer_backup(d: dict) -> dict:
    return {"Signer": d["Backup"], "Backup": d["Signer"]}
