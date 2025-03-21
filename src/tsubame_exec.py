import time
from typing import Literal, Union
from termcolor import colored
import fabric
from fabric import Connection
from invoke.exceptions import UnexpectedExit
from pathlib import Path
from patchwork.transfers import rsync
from string import Template


def make_connection(config: dict) -> Connection:
    conn_config = config["connection"]
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


def flatten_dict(dd, separator="_", prefix="") -> dict:
    return (
        {
            prefix + "_" + k if prefix else k: v
            for kk, vv in dd.items()
            for k, v in flatten_dict(vv, separator, kk).items()
        }
        if isinstance(dd, dict)
        else {prefix: dd}
    )


def format_cmd_str(cmds: Union[list, str], config: dict) -> str:
    if isinstance(cmds, str):
        cmds = [cmds]
    flat_dict = flatten_dict(config)
    return " && ".join(Template(i).substitute(flat_dict) for i in cmds)


def construct_script(config: dict) -> str:
    config = config["exec"]
    script_lines = [
        "#!/bin/sh",
        "#$ -cwd",
        # resource
        (
            f"#$ -l {config['resource']['type']}={config['resource']['count']}"
            if "resource" in config
            else ""
        ),
        # job name
        f"#$ -N {config['name']}" if "name" in config else "",
        (
            f"#$ -l h_rt={config['max_runtime']}"
            if "max_runtime" in config
            else ""
        ),
        # extra opts
        "\n".join([f"#$ {i}" for i in config.get("extra_options", [])]),
        # env vars
        "\n".join(
            [
                f"export {k}={v}"
                for k, v in config["env"].get("env_vars", {}).items()
            ]
        ),
        # modules
        "\n".join(
            [f"module load {i}" for i in config["env"].get("modules", [])]
        ),
        # python deps
        (
            "python3 -m pip install --user "
            + " ".join([i for i in config["env"]["python_deps"]])
            if "python_deps" in config["env"]
            and len(config["env"]["python_deps"]) > 0
            else ""
        ),
        # cmds
        format_cmd_str(config["cmd"], config)
    ]
    return "\n".join(script_lines) + "\n"


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
