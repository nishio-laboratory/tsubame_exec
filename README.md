# tsubame-exec

`tsubame-exec` is a simple script to automate running jobs on the [tsubame](https://en.wikipedia.org/wiki/Tsubame_(supercomputer)) supercomputer. In theory this should work on any machine supporting grid engine style qsub/qstat commands, but I have only tested this on tsubame.

Usage:
```bash
tsubame-exec -c config.toml
```

The format of the config.toml is as follows:
```toml
[connection]
host = "tsubame" # required, may use .ssh/config alias
username = "username"
password = "pw"

[sync.XXXXXX]
from = "~/local_path/"
to = "/gs/bs/tga-test/remote_path"
excludes = [".*", "__*"]

[exec]
cmd = "echo 'hello world'" # required, may be a list of multiple commands
max_runtime = "23:59:59"
name = "test_job"
group = "tga-test"

[exec.env]
dir = "tsubame_exec" # required, directory from which to run cmd
modules = ["intel", "cuda"]
python_deps = ["numpy", "matplotlib"]
env_vars = {TEST = 123}

[exec.env.resource]
type = "gpu_1"
count = 1 # default 1
```

## Notes

- You can have as many tables under the `sync` table as you like (as long as they have unique names).
  - For each one, `rsync` is called to sync the local `from` directory to the remote `to` directory on tsubame. I typically use two sync tables, one for code and one for data.
- Python dependencies specified in `exec.env.python_deps` are installed via pip, but this is subject to change.
- use `tsubame-exec -c config.toml --tail stdout` to submit the job and then watch the output
- define global options in `XDG_CONFIG_DIR/tsubame_exec/config.toml`. these options are merged with the config file every run. Use the global file to define, for instance, connection settings or syncs that should be run for every project.
