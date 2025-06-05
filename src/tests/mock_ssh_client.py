class Result:
    def __init__(self, status_code, output, cmd):
        self.status_code = status_code
        self.output = output
        self.cmd = cmd


class SshClient:
    def __init__(self):
        self.host_ip = "127.0.0.1"
        self.host_port = 22

    def run_cmd(self, cmd):
        return Result(0, "12", cmd)

    def run_local_cmd(self, cmd):
        return Result(0, "12", cmd)
