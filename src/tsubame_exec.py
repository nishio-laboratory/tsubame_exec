import time
from typing import Literal
from termcolor import colored
import textwrap
import fabric
from fabric import Connection
from invoke.exceptions import UnexpectedExit
from pathlib import Path
from patchwork.transfers import rsync

def make_connection(config: dict) -> Connection:
    conn_config = config["connection"]
    user = conn_config.get("username")
    password = conn_config.get("password")
    other = {"password": password} if password else {}
    return fabric.Connection(
        host=conn_config["host"],
        user=conn_config.get("username"),
        connect_kwargs=other,
    )


def sync_dir(conn: Connection, config: dict, key: str) -> None:
    src = Path(config["sync"][key]["from"])
    dst = config["sync"][key]["to"]
    excludes = config["sync"][key].get("excludes", [])
    print(colored(f"rsyncing {key} from {src} to tsubame:{dst}", "blue"))
    rsync(conn, src, dst, exclude=excludes)


def construct_script(config: dict) -> str:
    config = config["exec"]
    module_str = "\n".join(
        [f"module load {i}" for i in config["env"].get("modules", [])]
    )
    python_dep_str = (
        "python3 -m pip install --user "
        + " ".join([i for i in config["env"]["python_deps"]])
        if "python_deps" in config["env"]
        and len(config["env"]["python_deps"]) > 0
        else ""
    )
    env_var_str = "\n".join(
        [
            f"export {k}={v}"
            for k, v in config["env"].get("env_vars", {}).items()
        ]
    )
    out = f"""\
    #!/bin/sh
    #$ -cwd
    #$ -l {config["resource"]["type"]}={config["resource"]["count"]}
    #$ -l h_rt={config["max_runtime"]}
    #$ -N {config["name"]}
    {env_var_str}
    {module_str}
    {python_dep_str}
    {config["cmd"]}\
    """
    return textwrap.dedent(out)


def tail_status(
    conn: Connection,
    config: dict,
    job_id: int,
    tail: Literal["stderr", "stdout"],
):
    with conn.cd(config["exec"]["env"]["dir"]):
        start = time.time()
        filename = f"{config['exec']['name']}.{'o' if tail == 'stdout' else 'e'}{job_id}"
        while True:
            try:
                stat_o = conn.run(f"stat {filename}", hide=True)
                print(colored(f"job beginning!", "green"))
                break
            except UnexpectedExit:
                time_since_submit = time.strftime(
                    "%M:%S", time.gmtime(time.time() - start)
                )
                print(
                    colored(
                        f"waiting for job to begin... ({time_since_submit})",
                        "light_red",
                    )
                )
                time.sleep(1)
        conn.run(f"tail -f {filename}")
