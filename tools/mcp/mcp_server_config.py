class MCPServerConfig:
    def __init__(self, name: str, transport: str, command: str, args: list, port: int, description: str = None):
        self.name = name
        self.transport = transport 
        self.command = command
        self.args = args
        self.port = port
        self.description = description or f"{name} MCP Server"

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

    def get_description(self) -> str:
        return self.description

    def set_port(self, port: int):
        self.port = port
        
    def copy(self):
        return MCPServerConfig(
            name=self.name,
            transport=self.transport,
            command=self.command,
            args=self.args.copy(),
            port=self.port,
            description=self.description
        )