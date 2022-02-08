from dotenv import dotenv_values, find_dotenv
import os, csv


def create_data_path(pth: str, data_path: str = "data") -> os.path:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path, pth)
    if not os.path.exists(p):
        os.mkdir(p)
    return p


def parse_node_list(row: list, _http: str = "http", port: int = 9501) -> dict:
    signing = row[0]
    s_name = row[1]
    backup = row[2]
    b_name = row[3]
    return {
        "Signer": {"name": s_name, "ip": f"{_http}://{signing}:{port}"},
        "Backup": {"name": b_name, "ip": f"{_http}://{backup}:{port}"},
    }


def parse_monitors_list(row: list, _http: str = "http", port: int = 8000) -> dict:
    ip = row[0]
    name = row[1]
    return {"name": name, "ip": f"{_http}://{ip}:{port}"}


def parse_csv(_type: str = "nodes", fn: str = "node_pairs.csv", **kw) -> list:
    with open(os.path.join("includes", fn), newline="") as csvfile:
        d = []
        r = csv.reader(csvfile, delimiter=",")
        for row in r:
            if _type == "nodes":
                parsed = parse_node_list(row, **kw)
            else:
                parsed = parse_monitors_list(row, **kw)
            d.append(parsed)
        return d


class Envs:
    def __init__(self, **kw):
        self.load_envs()

    def load_envs(self):
        config = dotenv_values(find_dotenv())

        for k, v in config.items():
            if not v:
                raise ValueError(f"No value for key {k} - Please update .env file!")
            try:
                setattr(self, k, int(v))
            except (SyntaxError, ValueError):
                setattr(
                    self,
                    k,
                    True
                    if v.lower() == "true"
                    else False
                    if v.lower() == "false"
                    else v,
                )


def hot_reload_data(envs: Envs) -> tuple:
    # Hot reload Env
    envs.load_envs()
    # Pair up nodes that compliment each other.  Sames Keys, Different Nodes.
    #  if 1 goes down, the other will come up.
    nodes = parse_csv("nodes", **dict(port=envs.NODES_PORT, _http="http"))

    monitor_services = parse_csv(
        "monitor", fn="monitors.csv", **dict(port=envs.MONITOR_PORT, _http="http")
    )
    return nodes, monitor_services
