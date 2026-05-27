from src.core.options import options
class Sinks:
    __signature_lists = {
            'os_command': [
                'eval',
                "sink_hqbpillvul_execFile",
                'sink_hqbpillvul_exec',
                'sink_hqbpillvul_execSync',
                'sink_hqbpillvul_spawn',
                'sink_hqbpillvul_spawnSync',
                'sink_hqbpillvul_db',
                'exec',
                'execSync',
                'execFile',
                'execFileSync',
                'spawn',
                'spawnSync',
                'fork'
                ],
            'xss': [
                'pipe',
                'sink_hqbpillvul_http_write',
                'sink_hqbpillvul_http_setHeader',
                'write',
                'end',
                'send',
                'json',
                'jsonp',
                'render',
                'redirect',
                'setHeader'
                ],
            'proto_pollution': [
                'merge', 'extend', 'clone', 'parse'
                ],
            'code_exec': [
                'Function',
                'eval',
                "sink_hqbpillvul_execFile",
                'sink_hqbpillvul_exec',
                'sink_hqbpillvul_execSync',
                'sink_hqbpillvul_eval',
                'sink_hqbpillvul_code_execution',
                'setTimeout',
                'setInterval',
                'runInThisContext',
                'runInNewContext',
                'runInContext',
                'compileFunction'
                ],
            'sanitation': [
                'parseInt'
                ],
            'path_traversal': [
                'pipe',
                'sink_hqbpillvul_fs_read',
                'sink_hqbpillvul_http_sendFile',
                'read',
                'readFile',
                'readFileSync',
                'readdir',
                'readdirSync',
                'readlink',
                'readlinkSync',
                'readSync',
                'createReadStream',
                'writeFile',
                'writeFileSync',
                'appendFile',
                'appendFileSync',
                'createWriteStream',
                'sendFile',
                'download',
                'static',
                ],
            'depd': [
                'sink_hqbpillvul_pp',
                'sink_hqbpillvul_code_execution',
                'sink_hqbpillvul_exec'
                ]

    }

    def get_all_sign_list(self):
        """
        return a list of all the signature functions
        """
        res = []
        for key in self.__signature_lists:
            res += self.__signature_lists[key]

        return res

    def get_sinks_by_vul_type(self, vul_type, add_sinks=True):
        """
        return a list of sink functions by vul type
        """
        added_sinks = []
        if vul_type in self.__signature_lists:
            if add_sinks and options.add_sinks is not None:
                added_sinks = options.add_sinks.split(',')
            return self.__signature_lists[vul_type] + added_sinks
        return []
