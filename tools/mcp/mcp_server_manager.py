import json
import subprocess
import os
from mcp_server_config import MCPServerConfig

class MCPServerManager:
    def __init__(self):
        self.global_mcp_server_configs = {}
        self.groups = {}
        
        # 기본 그룹 생성
        self.groups["default"] = {"mcp_server_configs": {}}
        
        # config 파일 로드 및 초기화
        self._load_config()
        
        # 기본 그룹에 모든 서버 추가
        for server_name, config in self.global_mcp_server_configs.items():
            self.add_mcp_server_to_group("default", server_name)
            self.run_mcp_server("default",server_name)


    def _load_config(self):
        with open("mcp_config.json", "r") as f:
            config = json.load(f)
            
        for name, server_config in config["mcpServers"].items():
            # 기본 description 설정
            default_descriptions = {
                "cnu_data_mcp": "대학교 학과 학부 전공 강의 추천 및 관련 정보 조회, 강의계획서 조회에 특화된 도구",
                "interview_mcp": "대학교 전공 적성 및 역량 파악을 위한 인터뷰 정보 조회에 특화된 도구"
            }
            
            description = server_config.get("description") or default_descriptions.get(name, f"{name} MCP Server")
            
            mcp_config = MCPServerConfig(
                name=name,
                transport=server_config.get("transport"),
                command=server_config.get("command"),
                env=server_config.get("env"),
                args=server_config.get("args"),
                port=server_config.get("port"),
                description=description
            )
                    
            self.global_mcp_server_configs[name] = mcp_config

    def create_group(self, group_name: str):
        if group_name not in self.groups:
            self.groups[group_name] = {"mcp_server_configs": {}}

    def delete_group(self, group_name: str):
        if group_name != "default":
            self.groups.pop(group_name, None)

    def add_mcp_server_to_group(self, group_name: str, server_name: str):
        if group_name in self.groups and server_name in self.global_mcp_server_configs:
            self.groups[group_name]["mcp_server_configs"][server_name] = self.global_mcp_server_configs[server_name].copy()
            
            
            print(f"MCP 서버 '{server_name}'가 그룹 '{group_name}'에 추가되었습니다.")

    def remove_mcp_server_from_group(self, group_name: str, server_name: str):
        if group_name in self.groups:
            self.groups[group_name]["mcp_server_configs"].pop(server_name, None)

    def get_mcp_server_configs(self, group_name: str = "default") -> dict:
        return self.groups.get(group_name, {"mcp_server_configs": {}})["mcp_server_configs"]

    def get_multi_server_mcp_clients(self, group_name: str = "default") -> dict:
        result = {}
        configs = self.get_mcp_server_configs(group_name)
        
        for name, config in configs.items():
            result[name] = {
                "url": f"http://localhost:{config.get_port()}/{config.get_transport()}",
                "transport": config.get_transport(),
                "command": config.get_command(),
                "args": config.get_args(),
                "port": config.get_port(),
                "env": config.get_env()
            }
            
        return result
    def run_mcp_server(self, group_name: str, server_name: str):
        if server_name not in self.global_mcp_server_configs:
            raise ValueError(f"'{server_name}' MCP 서버를 찾을 수 없습니다.")
        
        config = self.groups[group_name]["mcp_server_configs"][server_name]
        command = config.get_command()
        args = config.get_args()

        try:
            # 현재 환경변수 복사
            env = os.environ.copy()
            
            if config.get_env():
                print(f"🔧 환경변수 설정: {config.get_env()}")
                env.update(config.get_env())
                print(f"🔧 환경변수 설정 완료: {env}")
            
            # 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
            if(command == "node"): # 노드일 경우
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # majorfree 디렉토리
            else:
                project_root = os.path.dirname(os.path.abspath(__file__)) # tools/mcp 디렉토리
            
            
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{project_root}:{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = project_root
                
            print(f"🔧 PYTHONPATH 설정: {env['PYTHONPATH']}")
            
            # 포트 사용중인 프로세스 확인 및 종료
            port = config.get_port()
            try:
                lsof = subprocess.check_output(f'lsof -ti:{port}', shell=True).decode()
                if lsof:
                    pid = lsof.strip()
                    subprocess.run(f'kill -9 {pid}', shell=True)
                    print(f"🔄 포트 {port}를 사용중이던 프로세스(PID: {pid})를 종료했습니다.")
            except subprocess.CalledProcessError:
                # 해당 포트를 사용중인 프로세스가 없는 경우
                pass
            
            process = subprocess.Popen(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                text=True,
                env=env,  # 환경변수 전달
                cwd=project_root  # 작업 디렉토리 설정
            )
            
            # 즉시 에러 체크
            import time
            time.sleep(2)  # 서버 시작 대기
            
            if process.poll() is not None:
                # 프로세스가 이미 종료됨
                stdout, stderr = process.communicate()
                print(f"❌ {server_name} 서버 실행 실패:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
            
            # 서버가 정상적으로 실행중인지 확인
            try:
                # 프로세스 상태 확인 
                if process.poll() is None:
                    # 서버 응답 확인을 위해 HTTP 요청 시도
                    import requests
                    from requests.exceptions import RequestException
                    
                    url = f"http://localhost:{port}/health"
                    max_retries = 5
                    retry_delay = 2
                    
                    for i in range(max_retries):
                        try:
                            response = requests.get(url, timeout=3)
                            if response.status_code == 200:
                                print(f"✅ {server_name} 서버가 정상적으로 응답합니다.")
                                break
                        except RequestException:
                            if i < max_retries - 1:
                                print(f"⏳ {server_name} 서버 응답 대기 중... ({i+1}/{max_retries})")
                                time.sleep(retry_delay)
                            else:
                                print(f"⚠️ {server_name} 서버가 응답하지 않습니다. 하지만 프로세스는 실행 중입니다.")
                else:
                    print(f"❌ {server_name} 서버 프로세스가 비정상적으로 종료되었습니다.")
                    return False
                    
            except Exception as e:
                print(f"⚠️ 서버 상태 확인 중 오류 발생: {e}")
                # 오류가 발생해도 프로세스가 실행 중이면 계속 진행
                if process.poll() is None:
                    print("프로세스는 계속 실행 중입니다.")
                else:
                    return False
                
                
            # 서버가 정상적으로 시작되었는지 확인
            print(f"{server_name} MCP 서버가 백그라운드에서 실행되었습니다. (PID: {process.pid})")
            
            # 실시간 로그 출력
            import threading
            def stream_output(pipe, prefix):
                for line in iter(pipe.readline, ''):
                    if line.strip():  # 빈 줄 제외
                        print(f"[{server_name}] {prefix}: {line.strip()}")
                        
            threading.Thread(target=stream_output, args=(process.stdout, "OUT"), daemon=True).start()
            threading.Thread(target=stream_output, args=(process.stderr,"error"), daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"MCP 서버 실행 중 오류 발생: {e}")
            return False

    
mcp_manager = MCPServerManager()