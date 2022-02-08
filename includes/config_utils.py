from dotenv import dotenv_values, find_dotenv
import os, csv


def create_data_path(pth: str, data_path: str = "data") -> os.path:
    cwd = os.getcwd()
    p = os.path.join(cwd, data_path, pth)
    if not os.path.exists(p):
        os.mkdir(p)
    return p


def parse_node_list(_http: str = "http", port: int = 9501) -> list:
    with open(os.path.join("includes", "node_pairs.csv"), newline="") as csvfile:
        d = []
        r = csv.reader(csvfile, delimiter=",")
        for row in r:
            signing = row[0]
            s_name = row[1]
            backup = row[2]
            b_name = row[3]
            d.append(
                {
                    "Signer": {"name": s_name, "ip": f"{_http}://{signing}:{port}"},
                    "Backup": {"name": b_name, "ip": f"{_http}://{backup}:{port}"},
                }
            )
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
