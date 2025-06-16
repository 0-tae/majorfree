class MCPServerConfig:
    def __init__(self, name: str, transport: str, command: str, args: list, port: int):
        self.name = name
        self.transport = transport 
        self.command = command
        self.args = args
        self.port = port

    def get_name(self) -> str:
        return self.name

    def get_transport(self) -> str:
        return self.transport

    def get_command(self) -> str:
        return self.command

    def get_args(self) -> list:
        return self.args

    def get_port(self) -> int:
        return self.port

    def set_port(self, port: int):
        self.port = port