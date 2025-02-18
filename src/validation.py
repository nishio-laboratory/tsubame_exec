from termcolor import colored


def validate_exec_config(config) -> None:
    if "name" not in config["exec"]:
        config["exec"]["name"] = "job.sh"
    if "resource" not in config["exec"]:
        config["exec"]["resource"] = {}
    if "max_runtime" not in config["exec"]["resource"]:
        print(
            colored(
                f"exec.max_runtime not defined. defaulting to 00:04:59", "red"
            )
        )
        config["exec"]["max_runtime"] = "23:59:59"
    if "type" not in config["exec"]["resource"]:
        print(
            colored(
                f"exec.resource.type not defined. defaulting to cpu_4", "red"
            )
        )
        config["exec"]["resource"]["type"] = "cpu_4"
    if "count" not in config["exec"]["resource"]:
        config["exec"]["resource"]["count"] = "1"
    if "group" not in config["exec"]["env"]:
        print(
            colored(
                "exec.env.group not specified. defaulting to tga-nlab", "red"
            )
        )
        config["exec"]["env"]["group"] = "tga-nlab"

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
    if config["exec"]["resource"]["type"] not in valid_resource_types:
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
