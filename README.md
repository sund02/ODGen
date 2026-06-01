# ODGen
ODGen is a JavaScript static analysis tool to detect vulnerabilities in Node.js packages. This project is written in Python and JavaScript and the source code is included in the repository. 

## Hello Reviewers
If you are the AE reviewer, please come here first! [README\_for\_AE\_reviewers.md](./README_for_AE_reviewers.md)

## Installation
Please check out [INSTALL.md](./INSTALL.md) for the detailed instruction of the installation.

## Project Extensions

This fork contains two focused improvements developed while reproducing the
ODGen artifact benchmark. Each improvement is kept on a separate branch so it
can be compared with the original implementation on `master`.

### Improved prototype pollution detection

Branch: [`improve-prototype-pollution`](https://github.com/sund02/ODGen/tree/improve-prototype-pollution)

The original implementation could miss a write such as:

```js
target[userKey] = userValue;
```

when `userKey` is attacker-controlled and may resolve to `__proto__`,
`constructor`, or `prototype`. The improved property handler checks whether a
tainted computed key may resolve to a built-in shared prototype while the
Object Dependence Graph is being constructed.

The targeted regression test is stored at:

```text
tests/packages/prototype_pollution/tainted-computed-proto-key.js
```

Run the test against the original implementation:

```bash
git switch master

docker run --rm \
  -v "$PWD/tests/packages/prototype_pollution/tainted-computed-proto-key.js:/case.js:ro" \
  iamthesong/odgen:latest bash -lc '
cd /root/projs/ODGen
rm -rf logs && mkdir -p logs
python odgen.py -t proto_pollution -maq /case.js --timeout 120
cat logs/succ.log
'
```

Run the same test against the improved implementation:

```bash
git switch improve-prototype-pollution

docker run --rm \
  -v "$PWD:/host-code:ro" \
  iamthesong/odgen:latest bash -lc '
cp /host-code/src/plugins/internal/handlers/property.py \
  /root/projs/ODGen/src/plugins/internal/handlers/property.py
cd /root/projs/ODGen
rm -rf logs && mkdir -p logs
python odgen.py -t proto_pollution -maq \
  /host-code/tests/packages/prototype_pollution/tainted-computed-proto-key.js \
  --timeout 120
cat logs/succ.log
'
```

Expected targeted-test result:

| Version | Detections |
| ------- | ---------- |
| Original `master` | 0 |
| `improve-prototype-pollution` | 1 |

Run the original prototype-pollution artifact benchmark:

```bash
git switch master
mkdir -p pp-artifact-master

docker run --rm \
  -v "$PWD/pp-artifact-master:/host-results" \
  iamthesong/odgen:latest bash -lc '
cd /root/projs/ODGen
rm -rf logs && mkdir -p logs
python odgen.py -t proto_pollution -maq \
  --list ./lists/proto_pollution.list --timeout 120
cp logs/succ.log /host-results/proto_pollution.succ.log
'
```

Run the improved prototype-pollution artifact benchmark:

```bash
git switch improve-prototype-pollution
mkdir -p pp-artifact-improved

docker run --rm \
  -v "$PWD:/host-code:ro" \
  -v "$PWD/pp-artifact-improved:/host-results" \
  iamthesong/odgen:latest bash -lc '
cp /host-code/src/plugins/internal/handlers/property.py \
  /root/projs/ODGen/src/plugins/internal/handlers/property.py
cd /root/projs/ODGen
rm -rf logs && mkdir -p logs
python odgen.py -t proto_pollution -maq \
  --list ./lists/proto_pollution.list --timeout 120
cp logs/succ.log /host-results/proto_pollution.succ.log
'
```

Then compare the logs:

```bash
diff pp-artifact-master/proto_pollution.succ.log \
     pp-artifact-improved/proto_pollution.succ.log
```

Artifact result:

| Version | Prototype-pollution reports |
| ------- | --------------------------- |
| Original `master` | 8 |
| `improve-prototype-pollution` | 17 |

The improved branch reported 9 additional packages. These are additional
static-analysis findings and have not been manually confirmed as true
positives.

### Broader source and sink coverage

Branch: [`improved-detection-coverage`](https://github.com/sund02/ODGen/tree/improved-detection-coverage)

This branch expands attacker-controlled sources such as HTTP request bodies,
query parameters, headers, cookies, command-line arguments, and environment
variables. It also adds commonly used sinks such as `execFileSync`, `fork`,
`spawnSync`, `res.send`, `res.json`, `sendFile`, `fs.readFile`,
`fs.createReadStream`, and `fs.writeFile`. The path-traversal rule now uses the
broader `has_user_input()` check instead of only checking a single URL
variable.

Run the grouped artifact benchmark on `master`:

```bash
git switch master
mkdir -p broader-artifact-original

docker run --rm \
  -v "$PWD/broader-artifact-original:/host-results" \
  iamthesong/odgen:latest bash -lc '
cd /root/projs/ODGen
for t in xss ipt path_traversal proto_pollution code_exec os_command
do
  rm -rf logs && mkdir -p logs
  python odgen.py -t "$t" -maq --list "./lists/$t.list" --timeout 120
  cp logs/succ.log "/host-results/$t.succ.log" || true
done
'
```

Run the same benchmark with the improved coverage files:

```bash
git switch improved-detection-coverage
mkdir -p broader-artifact-improved

docker run --rm \
  -v "$PWD:/host-code:ro" \
  -v "$PWD/broader-artifact-improved:/host-results" \
  iamthesong/odgen:latest bash -lc '
cd /host-code
cp --parents \
  builtin_packages/child_process.js \
  builtin_packages/express.js \
  builtin_packages/fs.js \
  builtin_packages/http.js \
  builtin_packages/https.js \
  builtin_packages/process.js \
  builtin_packages/ws.js \
  builtin_packages/yargs.js \
  src/core/checker.py \
  src/core/trace_rule.py \
  src/core/vul_func_lists.py \
  /root/projs/ODGen

cd /root/projs/ODGen
for t in xss ipt path_traversal proto_pollution code_exec os_command
do
  rm -rf logs && mkdir -p logs
  python odgen.py -t "$t" -maq --list "./lists/$t.list" --timeout 120
  cp logs/succ.log "/host-results/$t.succ.log" || true
done
'
```

Grouped artifact result:

| Vulnerability type | Original | Improved | Change |
| ------------------ | -------- | -------- | ------ |
| `xss` | 12 | 12 | 0 |
| `ipt` | 23 | 24 | +1 |
| `path_traversal` | 30 | 30 | 0 |
| `proto_pollution` | 8 | 8 | 0 |
| `code_exec` | 5 | 5 | 0 |
| `os_command` | 66 | 68 | +2 |

The broader coverage branch produced 3 additional artifact reports:
`solar@0.1.6` for internal property tampering, and
`git-revision-webpack-plugin@3.0.4` and `mysql-dumper@6.3.0` for command
injection. These reports have not been manually confirmed as true positives.

## Usage
Use the following arugments to run the tool:

```bash
python3 odgen.py	[-h] [-p] [-m] [-q] [-s] [-a] [--timeout TIMEOUT] [-l LIST] [--install] 
		[--max-rep MAX_REP] [--nodejs] [--pre-timeout PRE_TIMEOUT]
		[--max-file-stack MAX_FILE_STACK] [--skip-func SKIP_FUNC] [--run-env RUN_ENV] 
		[--no-file-based] [--parallel PARALLEL] [input_file]
```

| Argument | Description |
| -------- | ----------- |
| `input_file` | The path to the input file. It can be a Node.js package directory or a JavaScript file |
| `-t VUL_TYPE, --vul-type VUL_TYPE` | Set the vulneralbility type, for now, it can be "os\_command", "code\_exec", "proto\_pollution", "ipt", "xss" and "path\_traversal"|
| `-p, --print` | Print logs to console, instead of files. |
| `-m, --module` | Module mode. Indicate the input is a module, instead of a script. |
| `-q, --exit` | Exit the analysis immediately when vulnerability is found. Do not use this if you need a complete graph. |
| `-s, --single-branch` | Single branch mode (or single execution). If set, ODGen will disable the branch-sensitive mode. |
| `-a, --run-all` | Run all exported functions in module.exports of **all** analyzed files even if the file is not the entrance file.|
| `--timeout TIMEOUT`| The timeout(in seconds) of running a single module for one time. (Optimizations may run a module multiple times. This is the timeout for a single run.)|
| `-l, --list LIST`| Run a list of files/packages. Each line of the file contains the path to a file/package. |
| `--install`| Download the source code of a list of packages to the --run-env location. |
| `--max-rep MAX_REP`| If set, every function can only exsits in the call stack for at most MAX_REP times. (To prevent too many levels of recursive calls)| 
| `--nodejs`| Node.js mode. Indicate the input is a Node.js package. |
| `--pre-timeout PRE_TIMEOUT`| The timeout(in seconds) for preparing the environment before running the prioritized functions. Defaults to 30.|
| `--max-file-stack MAX_FILE_STACK`| The max depth of the required file stack. |
| `--skip-func SKIP_FUNC`| Skip a list of functions, separated by "," .|
| `--run-env ENV_DIR` | Set the running environment location.|
| `--add-sinks SINK_FUNCS` | If set, ODGen will treat the added function names as sink functions, separated by ","|
| `--no-file-based`| Only detect the vulnerabilities that can be directly accessed from the main entrance of the package. |
| `--parallel PARALLEL`| Run a list of packages parallelly in PARALLEL threads. Only works together with --list argument. |

Once the command is finished, the tool will output the detecting result, and if any vulnerability is found, it will also output the location of the vulnerability and the attack path. 

### Command-line example
Here is an example to show how to use our command-line based tool:

```shell
$ python3 ./odgen.py ./tests/packages/command_injection/os_command.js -m -a -q -t os_command
```

Or to analyze a Node.js package, you can run a command like:

```shell
$ python3 ./odgen.py ./tests/packages/prototype_pollution/confucious@0.0.12 -maq -t proto_pollution
```

We also create a sample module with a prototype pollution vulnerability. You can test it by running:

```shell
$ python3 ./odgen.py ./tests/packages/prototype_pollution/pp.js -m -a -q -t proto_pollution
```

In this example, the output of the command-line based interface will be like:

```bash
Prototype pollution detected at node 49 (Line 4)
|Checker| Dataflow of Object Property:
Attack Path:
==========================
$FilePath$ODGen/tests/packages/pp.js
Line 11	function pp(key1, key2, value) {
$FilePath$ODGen/tests/packages/pp.js
Line 7	  var mid = val + " ";
$FilePath$ODGen/tests/packages/pp.js
Line 4	  proto[key2] = value;


|Checker| Dataflow of Assigned Value:
Attack Path:
==========================
$FilePath$ODGen/tests/packages/pp.js
Line 11	function pp(key1, key2, value) {
$FilePath$ODGen/tests/packages/pp.js
Line 4	  proto[key2] = value;


|Checker| Polluted Built-in Prototype:
Attack Path:
==========================
$FilePath$None
Object.prototype
$FilePath$ODGen/tests/packages/pp.js
Line 4	  proto[key2] = value;
```

Note that **ODGen** only outputs data-flows, which means that a statement is included in the path only when a new **object** is created and the created object will influence the result. For example, line 7 is included in the result because at line 7, *val + " "* creates a new object. While at line 12, even *tmp* is a new variable, it points to the created object at line 7, and no new object is created at line 12, **ODGen** will not include this statement in the result. 
