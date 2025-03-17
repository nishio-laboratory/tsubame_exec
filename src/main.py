import argparse
import io
import re
import toml
import platformdirs
from pathlib import Path
from tsubame_exec import *
import validation


def main():
    args = parse_args()
    config = parse_config(args)
    conn = make_connection(config)

    validation.validate_minimal(config)

    if args.tsubame_validation or config.get("tsubame_validation"):
        validation.validate_exec_config(config)

    for key in config["sync"]:
        validation.validate_sync(config["sync"][key], key)
        sync_dir(conn, config, key)

    exec_dir = config["exec"]["env"]["dir"]
    conn.run(f"mkdir -p {exec_dir}")
    conn.put(io.StringIO(construct_script(config)), exec_dir + "/job.sh")
    with conn.cd(exec_dir):
        group_str = (
            f"-g {config['exec']['group']}"
            if "group" in config["exec"]
            else ""
        )
        submit_stdo_matches = re.search(
            r"Your job (\d+)",
            conn.run(f'bash -c "qsub job.sh {group_str}"', hide=True).stdout,
        )
        if submit_stdo_matches is None:
            raise Exception("could not parse job_id from submit response")
        else:
            job_id = int(submit_stdo_matches.group(1))
        print(colored(f"successfully submitted job id {job_id}!", "green"))

    if args.tail:
        tail_status(conn, config, job_id, args.tail)


def parse_config(args):
    config = toml.load(args.config)
    global_config_path = (
        platformdirs.user_config_path() / "tsubame_exec" / "config.toml"
    )
    if global_config_path.exists():
        global_config = toml.load(global_config_path)
        config |= global_config
    return config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, type=Path)
    parser.add_argument("--tsubame-validation", action="store_true")
    parser.add_argument("--tail", default=False)
    args = parser.parse_args()

    if args.tail and args.tail != "stderr" and args.tail != "stdout":
        raise Exception(
            "--tail specified but argument must be 'stderr' or 'stdout'"
        )

    return args


if __name__ == "__main__":
    main()
