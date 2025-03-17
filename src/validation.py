from termcolor import colored
import datetime


def validate_exec_config(config) -> None:
    if "name" not in config["exec"]:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(
            colored(
                f"[warning] exec.name not specified, defaulting to 'job_{now}'",
                "red",
            )
        )
        config["exec"]["name"] = f"job_{now}"
    if "resource" not in config["exec"]:
        config["exec"]["resource"] = {}
    if "max_runtime" not in config["exec"]:
        print(
            colored(
                f"[warning] exec.max_runtime not defined. defaulting to 00:05:00",
                "red",
            )
        )
        config["exec"]["max_runtime"] = "00:05:00"
    if isinstance(config["exec"]["max_runtime"], datetime.time):
        config["exec"]["max_runtime"] = config["exec"]["max_runtime"].strftime(
            "%H:%M:%S"
        )
    if "type" not in config["exec"]["resource"]:
        print(
            colored(
                f"[warning] exec.resource.type not specified! defaulting to cpu_4",
                "red",
            )
        )
        config["exec"]["resource"]["type"] = "cpu_4"

    if "count" not in config["exec"]["resource"]:
        print(colored("[warning]: exec.resource.count not specified!", "red"))
        config["exec"]["resource"]["count"] = "1"

    if "group" not in config["exec"]:
        print(colored("[warning]: exec.group not specified!", "red"))

    valid_resource_types = [
        "node_f",
        "node_h",
        "node_q",
        "node_o",
        "gpu_1",
        "gpu_h",
        "cpu_160",
        "cpu_80",
        "cpu_40",
        "cpu_16",
        "cpu_8",
        "cpu_4",
    ]
    if (
        "type" in config["exec"]["resource"]
        and config["exec"]["resource"]["type"] not in valid_resource_types
    ):
        valid_types_str = "\n".join(valid_resource_types)
        raise Exception(
            f"resource type {config['exec']['resource']['type']} not valid; must be one of: \n {valid_types_str}"
        )


def validate_sync(sync_config: dict, key: str) -> None:
    if "from" not in sync_config:
        raise Exception(f"sync.{key} is defined with no 'from' key")
    if "to" not in sync_config:
        raise Exception(f"sync.{key} is defined with no 'to' key")


def validate_minimal(config: dict) -> None:
    if "exec" not in config:
        raise Exception(
            "exec table not defined. you must at minimum specify exec.cmd and exec.env.dir"
        )
    if "env" not in config["exec"]:
        raise Exception(
            "exec.env table not defined. you must specify exec.env.dir"
        )
    if "dir" not in config["exec"]["env"]:
        raise Exception("you must specify exec.env.dir")
    if "cmd" not in config["exec"]:
        raise Exception("you must specify exec.cmd")
