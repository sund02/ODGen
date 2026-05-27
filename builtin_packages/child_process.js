function exec(command, callback1='nobk',callback2='nobk') {
  var err = 'err';
  var stdout = 'stdout';
  var stderr = 'stderr';
  var sink = command;
  sink_hqbpillvul_exec(sink);
  callback1(err, stdout, stderr);
  callback2(err, stdout, stderr);
}

function execSync(command, options='nothing',callback='nobk') {
  var err = 'err';
  var stdout = 'stdout';
  var stderr = 'stderr';
  var sink = command;
  sink_hqbpillvul_execSync(sink);
  callback(err, stdout, stderr);
}

function execFile(command, options='nothing', dict='nothing', callback='nobk') {
  var err = 'err';
  var stdout = 'stdout';
  var stderr = 'stderr';
  var sink = command;
  sink_hqbpillvul_execFile(sink);
  callback(err, stdout, stderr);
}

function execFileSync(command, options='nothing', dict='nothing') {
  var sink = command;
  sink_hqbpillvul_execFile(sink);
  return 'stdout';
}

function spawn(command, args='nothing', options='nothion') {
  sink_hqbpillvul_spawn(command);
}

function spawnSync(command, args='nothing', options='nothion') {
  sink_hqbpillvul_spawnSync(command);
}

function fork(modulePath, args='nothing', options='nothing') {
  sink_hqbpillvul_spawn(modulePath);
}


module.exports = {
  exec,
  execFile,
  execFileSync,
  execSync,
  spawn,
  spawnSync,
  fork
}
