# tsubame-exec

`tsubame-exec` is a simple script to automate running jobs on the
[tsubame](https://en.wikipedia.org/wiki/Tsubame_(supercomputer))
supercomputer. In theory this should work on any machine supporting
grid engine style qsub/qstat commands, but I have only tested this on
tsubame.

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
max_runtime = 23:59:59 # may also be a str
name = "test_job"
group = "tga-test"
extra_options = ["-p PRIORITY"]

[exec.env]
dir = "tsubame_exec" # required, directory from which to run cmd
modules = ["intel", "cuda"]
python_deps = ["numpy", "matplotlib"]
env_vars = {TEST = 123}

[exec.resource]
type = "gpu_1"
count = 1 # default 1
```
In this case, `tsubame-exec` will:

1. ssh into the remote machine specified in `connection`
2. For every table under `sync`:
  1. Call rsync to sync local directory `sync.XXX.from` to remote
     directory `sync.XXX.to`
3. cd into `exec.env.dir`
4. Generate a script `job.sh` based on the fields in table `exec`
5. Run `qsub job.sh` and return the job id


## Notes
- You can have as many tables under the `sync` table as you like (as long as they have unique names).
- Python dependencies specified in `exec.env.python_deps` are installed via pip, but this is subject to change.
- `tsubame-exec -c config.toml --tsubame-validation` is equivalent to including `tsubame_validation = true` in the top level of your `config.toml`. Use this option to invoke tsubame-specific safety checks.
- define global options in `XDG_CONFIG_DIR/tsubame_exec/config.toml`. these options are merged with the config file every run. Use the global file to define, for instance, connection settings or syncs that should be run for every project.
- Use `tsubame-exec --tail {stdout/stderr}` to wait for a job to submit and then follow a stream. there is currently no checking to see whether a job has finished, so this will block, use ctrl-c to exit. I suggest printing a message in your code to notify completion.
- Some keys support string templating using `string.Template`. The `exec` table gets flattened
(in the case of nested dictionaries, the key names are joined by '_'). So, to use the resource type, use `cmd = "echo $resource_type"`. `exec.name` is templated first, followed by `exec.env.dir`, and then finally `exec.cmd`. This order is chosen with purpose; it makes it possible to define a hyperparameter in the `exec` table, and then automatically change the job name and create a new directory for your run files.


## For non-tsubame users
- `exec.max_runtime` translates to `#$ -l h_rt=TIME` in the generated script
- I suspect that most use cases can be covered with the `exec.extra_options` list. Each one is simply prefixed with `#$` and inserted into the generated script

## TODO
- Tests
