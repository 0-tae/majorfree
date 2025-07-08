// 대시보드 JavaScript 기능

// Markdown 파싱 함수
function parseMarkdown(text) {
    // null, undefined, 빈 문자열 체크
    if (!text || text === null || text === undefined) {
        return '';
    }
    
    if (typeof marked !== 'undefined') {
        return marked.parse(text);
    }
    // marked가 없으면 기본 텍스트 반환
    return escapeHtml(text).replace(/\n/g, '<br>');
}

// MCP 서버 목록 로드
async function loadMcpServers() {
    try {
        const response = await fetch('/api/mcp-servers');
        const result = await response.json();
        
        // HttpResponse 형식 처리
        const servers = result.item || [];
        
        const container = document.getElementById('mcpServers');
        if (servers.length === 0) {
            container.innerHTML = '<div class="alert alert-info">MCP 서버가 없습니다.</div>';
            return;
        }
        
        let html = '<div class="row">';
        
        servers.forEach(server => {
            const statusBadge = server.is_running ? 
                '<span class="badge bg-success">실행 중</span>' : 
                '<span class="badge bg-danger">중지됨</span>';
            
            const description = server.description.length > 100 ? 
                server.description.substring(0, 100) + '...' : server.description;
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <i class="fas fa-server me-2"></i>${server.server_name}
                            </h6>
                            ${statusBadge}
                        </div>
                        <div class="card-body">
                            <h6 class="card-title">${server.name}</h6>
                            <p class="card-text"><small>${escapeHtml(description)}</small></p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>
                                    ${server.updated_at ? new Date(server.updated_at).toLocaleString() : '업데이트 없음'}
                                </small>
                                <a href="/mcp/${server.server_name}" class="btn btn-primary btn-sm">
                                    <i class="fas fa-cog me-1"></i>관리
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    } catch (error) {
        console.error('MCP 서버 목록 로드 실패:', error);
        document.getElementById('mcpServers').innerHTML = 
            '<div class="alert alert-danger">서버 목록 로드 중 오류가 발생했습니다.</div>';
    }
}

// SQL Agent 로그 로드 (페이지네이션) - request_id 그룹화
async function loadSqlAgentLogs(page = 1) {
    try {
        const response = await fetch(`/api/sql-agent/logs/request-groups?page=${page}`);
        const result = await response.json();
        
        // HttpResponse 형식 처리
        const data = result.item || {};
        
        const container = document.getElementById('sqlAgentLogs');
        if (!data.logs || data.logs.length === 0) {
            container.innerHTML = '<div class="alert alert-info">SQL Agent 로그가 없습니다.</div>';
            return;
        }
        
        let html = `<div class="mb-3">
            <strong>Request ID:</strong> <code>${data.request_id}</code>
            <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${data.request_id}')">
                <i class="fas fa-copy"></i>
            </button>
        </div>`;
        html += '<div class="table-responsive"><table class="table table-striped table-sm">';
        html += '<thead><tr><th>Request ID</th><th>단계</th><th>도구</th><th>입력</th><th>출력</th><th>시간</th></tr></thead><tbody>';
        
        data.logs.forEach(logArray => {
            const log = convertSqlLogArrayToObject(logArray);
            const toolInput = log.tool_input;
            const toolOutput = log.tool_output;
            const request_id = log.request_id || 'N/A';
            const inputId = 'sql_input_' + log.id;
            const outputId = 'sql_output_' + log.id;
            
            html += `
                <tr>
                    <td><code class="small">${request_id !== 'N/A' ? request_id.substring(0, 8) + '...' : 'N/A'}</code></td>
                    <td><span class="badge bg-secondary">${log.step_order}</span></td>
                    <td><code>${escapeHtml(log.tool_name)}</code></td>
                    <td>
                        <div id="${inputId}" class="log-content collapsed">
                            ${escapeHtml(toolInput)}
                        </div>
                        <small><a href="#" class="expand-text" onclick="toggleContent('${inputId}')">전체 보기</a></small>
                    </td>
                    <td>
                        <div id="${outputId}" class="log-content collapsed">
                            ${escapeHtml(toolOutput)}
                        </div>
                        <small><a href="#" class="expand-text" onclick="toggleContent('${outputId}')">전체 보기</a></small>
                    </td>
                    <td><small>${new Date(log.created_at).toLocaleString()}</small></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
        // 페이지네이션 렌더링
        renderPagination('sqlAgentPagination', data, (page) => loadSqlAgentLogs(page));
    } catch (error) {
        console.error('SQL Agent 로그 로드 실패:', error);
        document.getElementById('sqlAgentLogs').innerHTML = 
            '<div class="alert alert-danger">로그 로드 중 오류가 발생했습니다.</div>';
    }
}

// MCP 서버 로그 로드 (페이지네이션) - request_id 그룹화도 지원
async function loadMcpLogs(page = 1) {
    try {
        const perPage = document.getElementById('mcpPerPage')?.value || 10;
        
        // request_id 그룹화 모드인지 일반 모드인지 확인
        const useGroupMode = document.getElementById('mcpGroupMode')?.checked || false;
        
        let response, result, data;
        if (useGroupMode) {
            response = await fetch(`/api/mcp-logs/request-groups?page=${page}`);
            result = await response.json();
            // HttpResponse 형식 처리
            data = result.item || {};
        } else {
            response = await fetch(`/api/mcp-logs/paginated?page=${page}&per_page=${perPage}`);
            result = await response.json();
            // HttpResponse 형식 처리
            data = result.item || {};
        }
        
        const container = document.getElementById('mcpLogs');
        if (!data.logs || data.logs.length === 0) {
            container.innerHTML = '<div class="alert alert-info">MCP 서버 로그가 없습니다.</div>';
            return;
        }
        
        let html = '';
        
        // 그룹 모드일 때 Request ID 표시
        if (useGroupMode && data.request_id) {
            html += `<div class="mb-3">
                <strong>Request ID:</strong> <code>${data.request_id}</code>
                <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${data.request_id}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>`;
        }
        
        html += '<div class="table-responsive"><table class="table table-striped table-sm">';
        html += '<thead><tr>';
        if (!useGroupMode) html += '<th>Request ID</th>';
        html += '<th>서버</th><th>이름</th><th>지시사항</th><th>답변</th><th>시간</th></tr></thead><tbody>';
        
        data.logs.forEach(logArray => {
            const log = convertLogArrayToObject(logArray);
            const instruction = log.instruction;
            const answer = log.answer;
            const request_id = log.request_id || 'N/A';
            const instructionId = 'mcp_inst_' + log.id;
            const answerId = 'mcp_ans_' + log.id;
            
            html += `
                <tr>`;
            if (!useGroupMode) {
                html += `<td><code class="small">${request_id !== 'N/A' ? request_id.substring(0, 8) + '...' : 'N/A'}</code></td>`;
            }
            html += `
                    <td><span class="badge bg-primary">${log.mcp_server}</span></td>
                    <td>${escapeHtml(log.name)}</td>
                    <td>
                        <div id="${instructionId}" class="log-content collapsed">
                            ${escapeHtml(instruction)}
                        </div>
                        <small><a href="#" class="expand-text" onclick="toggleContent('${instructionId}')">전체 보기</a></small>
                    </td>
                    <td>
                        <div id="${answerId}" class="log-content collapsed markdown-content">
                            ${parseMarkdown(answer)}
                        </div>
                        <small><a href="#" class="expand-text" onclick="toggleContent('${answerId}')">전체 보기</a></small>
                    </td>
                    <td><small>${new Date(log.created_at).toLocaleString()}</small></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
        // 페이지네이션 렌더링
        renderPagination('mcpLogsPagination', data, (page) => loadMcpLogs(page));
    } catch (error) {
        console.error('MCP 로그 로드 실패:', error);
        document.getElementById('mcpLogs').innerHTML = 
            '<div class="alert alert-danger">로그 로드 중 오류가 발생했습니다.</div>';
    }
}

// 클립보드에 복사
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // 간단한 토스트 알림
        const toast = document.createElement('div');
        toast.className = 'position-fixed top-0 end-0 p-3';
        toast.style.zIndex = '1050';
        toast.innerHTML = `
            <div class="toast show" role="alert">
                <div class="toast-body">
                    Request ID가 클립보드에 복사되었습니다!
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 2000);
    });
}

// 로그 내용 확장/축소
function toggleContent(elementId) {
    const element = document.getElementById(elementId);
    const link = element.nextElementSibling.querySelector('a');
    
    if (element.classList.contains('collapsed')) {
        element.classList.remove('collapsed');
        element.classList.add('expanded');
        link.textContent = '축소';
    } else {
        element.classList.remove('expanded');
        element.classList.add('collapsed');
        link.textContent = '전체 보기';
    }
}

// 페이지네이션 렌더링
function renderPagination(containerId, data, onPageClick) {
    const container = document.getElementById(containerId);
    if (!data || data.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<nav><ul class="pagination pagination-sm justify-content-center">';
    
    // 이전 페이지
    if (data.has_prev) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="event.preventDefault(); (${onPageClick})(${data.current_page - 1})">이전</a></li>`;
    }
    
    // 페이지 번호들
    for (let i = Math.max(1, data.current_page - 2); i <= Math.min(data.total_pages, data.current_page + 2); i++) {
        const active = i === data.current_page ? 'active' : '';
        html += `<li class="page-item ${active}"><a class="page-link" href="#" onclick="event.preventDefault(); (${onPageClick})(${i})">${i}</a></li>`;
    }
    
    // 다음 페이지
    if (data.has_next) {
        html += `<li class="page-item"><a class="page-link" href="#" onclick="event.preventDefault(); (${onPageClick})(${data.current_page + 1})">다음</a></li>`;
    }
    
    html += '</ul></nav>';
    container.innerHTML = html;
}

// 유틸리티 함수들
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 배열 형태의 로그를 객체로 변환하는 함수
function convertLogArrayToObject(logArray) {
    // MCP 로그 배열 구조: [id, mcp_server, name, description, instruction, prompt, answer, created_at, updated_at, request_id]
    if (Array.isArray(logArray)) {
        return {
            id: logArray[0],
            mcp_server: logArray[1],
            name: logArray[2],
            description: logArray[3],
            instruction: logArray[4],
            prompt: logArray[5],
            answer: logArray[6],
            created_at: logArray[7],
            updated_at: logArray[8],
            request_id: logArray[9]
        };
    }
    return logArray; // 이미 객체인 경우 그대로 반환
}

// SQL Agent 로그 배열을 객체로 변환하는 함수
function convertSqlLogArrayToObject(logArray) {
    // SQL Agent 로그 배열 구조: [id, instruction, tool_name, tool_input, tool_output, step_order, created_at, updated_at, request_id]
    if (Array.isArray(logArray)) {
        return {
            id: logArray[0],
            instruction: logArray[1],
            tool_name: logArray[2],
            tool_input: logArray[3],
            tool_output: logArray[4],
            step_order: logArray[5],
            created_at: logArray[6],
            updated_at: logArray[7],
            request_id: logArray[8]
        };
    }
    return logArray; // 이미 객체인 경우 그대로 반환
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 초기 로그 및 서버 목록 로드
    loadSqlAgentLogs(1);
    loadMcpLogs(1);
    loadMcpServers();
}); 