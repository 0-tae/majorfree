// MCP 서버 개별 페이지 JavaScript
const serverName = window.location.pathname.split('/').pop();
let currentInstruction = '';
let currentRequestId = '';

// Markdown 파싱 함수
function parseMarkdown(text) {
    if (typeof marked !== 'undefined') {
        return marked.parse(text);
    }
    // marked가 없으면 기본 텍스트 반환
    return escapeHtml(text).replace(/\n/g, '<br>');
}

// 서버 정보 로드
async function loadServerInfo() {
    try {
        const response = await fetch(`/api/mcp-servers/${serverName}`);
        const server = await response.json();
        
        const statusBadge = server.is_running ? 
            '<span class="badge bg-success">실행 중</span>' : 
            '<span class="badge bg-danger">중지됨</span>';
        
        document.getElementById('serverInfo').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>서버 이름:</strong> ${server.server_name}</p>
                    <p><strong>이름:</strong> ${server.name}</p>
                    <p><strong>포트:</strong> ${server.port}</p>
                    <p><strong>상태:</strong> ${statusBadge}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>설명:</strong></p>
                    <p>${server.description}</p>
                    <p><strong>프롬프트:</strong></p>
                    <p>${server.prompt || '없음'}</p>
                </div>
            </div>
        `;
        
        // 폼 필드 설정
        document.getElementById('serverName').value = server.name;
        document.getElementById('serverDescription').value = server.description;
        document.getElementById('serverPrompt').value = server.prompt || '';
    } catch (error) {
        console.error('서버 정보 로드 실패:', error);
    }
}

// 서버 로그 로드 (페이지네이션)
async function loadServerLogs(page = 1) {
    try {
        const perPage = document.getElementById('mcpPerPage')?.value || 10;
        const response = await fetch(`/api/mcp-logs/paginated?server_name=${serverName}&page=${page}&per_page=${perPage}`);
        const data = await response.json();
        
        const container = document.getElementById('serverLogs');
        if (data.logs.length === 0) {
            container.innerHTML = '<div class="alert alert-info">로그가 없습니다.</div>';
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table table-striped table-sm">';
        html += '<thead><tr><th>Request ID</th><th>이름</th><th>지시사항</th><th>답변</th><th>시간</th></tr></thead><tbody>';
        
        data.logs.forEach(log => {
            const instruction = log[4]; // instruction
            const answer = log[6]; // answer
            const request_id = log[9]; // request_id (새로 추가된 컬럼)
            const instructionId = 'inst_' + log[0];
            const answerId = 'ans_' + log[0];
            
            html += `
                <tr>
                    <td><code class="small">${request_id ? request_id.substring(0, 8) + '...' : 'N/A'}</code></td>
                    <td>${escapeHtml(log[2])}</td>
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
                    <td><small>${new Date(log[7]).toLocaleString()}</small></td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
        // 페이지네이션 렌더링
        renderPagination('serverLogsPagination', data, (page) => loadServerLogs(page));
    } catch (error) {
        console.error('로그 로드 실패:', error);
    }
}

// 현재 실행 결과 로드
async function loadCurrentExecutionResults(instruction) {
    const resultContainer = document.getElementById('currentExecutionResult');
    const mcpContainer = document.getElementById('currentMcpResult');
    const sqlContainer = document.getElementById('currentSqlLogs');
    const sqlPaginationContainer = document.getElementById('currentSqlLogsPagination');
    
    resultContainer.style.display = 'block';
    
    try {
        // 특정 instruction에 대한 가장 최근 MCP 서버 로그 조회
        const mcpResponse = await fetch(`/api/mcp-logs/latest?instruction=${encodeURIComponent(instruction)}&server_name=${serverName}`);
        const mcpLogs = await mcpResponse.json();
        
        if (mcpLogs.length > 0) {
            const log = mcpLogs[0];
            const request_id = log[9]; // request_id는 인덱스 9에 위치
            currentRequestId = request_id;
            
            // 같은 request_id를 가진 모든 MCP 로그 가져오기
            if (request_id) {
                const allMcpResponse = await fetch(`/api/mcp-logs/by-request/${request_id}`);
                const allMcpLogs = await allMcpResponse.json();
                
                let mcpHtml = `<div class="mb-2">
                    <strong>Request ID:</strong> <code>${request_id}</code>
                    <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${request_id}')">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>`;
                
                if (allMcpLogs.length > 1) {
                    // 여러 개의 MCP 로그가 있으면 accordion으로 표시
                    mcpHtml += '<div class="accordion" id="mcpAccordion">';
                    allMcpLogs.forEach((mcpLog, index) => {
                        mcpHtml += `
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="mcpHeading${index}">
                                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#mcpCollapse${index}">
                                        ${escapeHtml(mcpLog[2])} - ${new Date(mcpLog[7]).toLocaleString()}
                                    </button>
                                </h2>
                                <div id="mcpCollapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" data-bs-parent="#mcpAccordion">
                                    <div class="accordion-body">
                                        <p><strong>지시사항:</strong> ${escapeHtml(mcpLog[4])}</p>
                                        <div class="markdown-content">${parseMarkdown(mcpLog[6])}</div>
                                        <small class="text-muted">${new Date(mcpLog[7]).toLocaleString()}</small>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    mcpHtml += '</div>';
                } else {
                    // 하나의 로그만 있으면 단일 카드로 표시
                    const mcpLog = allMcpLogs[0];
                    mcpHtml += `
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">${escapeHtml(mcpLog[2])}</h6>
                                <p><strong>지시사항:</strong> ${escapeHtml(mcpLog[4])}</p>
                                <div class="markdown-content">${parseMarkdown(mcpLog[6])}</div>
                                <small class="text-muted">${new Date(mcpLog[7]).toLocaleString()}</small>
                            </div>
                        </div>
                    `;
                }
                
                mcpContainer.innerHTML = mcpHtml;
            } else {
                mcpContainer.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${escapeHtml(log[2])}</h6>
                            <p><strong>지시사항:</strong> ${escapeHtml(log[4])}</p>
                            <div class="markdown-content">${parseMarkdown(log[6])}</div>
                            <small class="text-muted">${new Date(log[7]).toLocaleString()}</small>
                        </div>
                    </div>
                `;
            }
            
            // 동일한 request_id에 해당하는 SQL Agent 로그 로드
            if (request_id) {
                await loadLatestSqlAgentLogs(sqlContainer, sqlPaginationContainer, request_id);
            } else {
                sqlContainer.innerHTML = '<div class="alert alert-warning">Request ID가 없어 SQL Agent 로그를 로드할 수 없습니다.</div>';
                sqlPaginationContainer.innerHTML = '';
            }
        } else {
            mcpContainer.innerHTML = '<div class="alert alert-info">실행 결과가 없습니다.</div>';
            sqlContainer.innerHTML = '<div class="alert alert-info">실행 로그가 없습니다.</div>';
            sqlPaginationContainer.innerHTML = '';
        }
        
    } catch (error) {
        console.error('현재 실행 결과 로드 실패:', error);
        mcpContainer.innerHTML = '<div class="alert alert-danger">MCP 결과 로드 중 오류가 발생했습니다.</div>';
        sqlContainer.innerHTML = '<div class="alert alert-danger">SQL Agent 로그 로드 중 오류가 발생했습니다.</div>';
    }
}

// 최신 request_id에 해당하는 SQL Agent 로그를 로드
async function loadLatestSqlAgentLogs(container = null, paginationContainer = null, request_id = null) {
    try {
        const response = await fetch('/api/sql-agent/logs/latest-by-request-id');
        const logs = await response.json();
        
        const targetContainer = container || document.getElementById('currentSqlLogs');
        const targetPaginationContainer = paginationContainer || document.getElementById('currentSqlLogsPagination');
        
        if (logs.length === 0) {
            targetContainer.innerHTML = '<div class="alert alert-info">실행 로그가 없습니다.</div>';
            targetPaginationContainer.innerHTML = '';
            return;
        }
        
        // 첫 번째 로그에서 request_id를 가져옵니다 (모든 로그가 같은 request_id를 가짐)
        const actualRequestId = request_id || logs[0][8]; // request_id는 인덱스 8에 위치
        
        let sqlHtml = `<div class="mb-2">
            <strong>Request ID:</strong> <code>${actualRequestId}</code>
            <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${actualRequestId}')">
                <i class="fas fa-copy"></i>
            </button>
        </div>`;
        sqlHtml += '<div class="accordion" id="sqlAccordion">';
        
        logs.forEach((log, index) => {
            sqlHtml += `
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading${index}">
                        <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                            단계 ${log[5]} - ${escapeHtml(log[2])}
                        </button>
                    </h2>
                    <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" data-bs-parent="#sqlAccordion">
                        <div class="accordion-body">
                            <p><strong>입력:</strong></p>
                            <pre><code>${escapeHtml(log[3])}</code></pre>
                            <p><strong>출력:</strong></p>
                            <pre><code>${escapeHtml(log[4])}</code></pre>
                            <small class="text-muted">${new Date(log[7]).toLocaleString()}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        sqlHtml += '</div>';
        targetContainer.innerHTML = sqlHtml;
        
        // 현재 실행 결과에서는 페이지네이션 불필요 (한 번의 실행 결과만 표시)
        targetPaginationContainer.innerHTML = '';
        
    } catch (error) {
        console.error('SQL Agent 로그 로드 실패:', error);
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">로그 로드 중 오류가 발생했습니다.</div>';
        }
    }
}

// 특정 request_id에 해당하는 SQL Agent 로그를 로드 (기존 함수명 유지)
async function loadSqlAgentLogsByRequestId(request_id, container = null, paginationContainer = null) {
    await loadLatestSqlAgentLogs(container, paginationContainer, request_id);
}

// 서버 정보 업데이트
async function updateServerInfo(event) {
    event.preventDefault();
    
    const formData = {
        server_name: serverName,
        name: document.getElementById('serverName').value,
        description: document.getElementById('serverDescription').value,
        prompt: document.getElementById('serverPrompt').value
    };
    
    try {
        const response = await fetch('/api/mcp-servers/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('서버 정보가 성공적으로 업데이트되었습니다.');
            loadServerInfo();
        } else {
            alert('서버 정보 업데이트 실패: ' + result.detail);
        }
    } catch (error) {
        console.error('서버 업데이트 실패:', error);
        alert('서버 업데이트 중 오류가 발생했습니다.');
    }
}

// 서버 실행
async function executeServer(event) {
    event.preventDefault();
    
    const instruction = document.getElementById('instruction').value;
    currentInstruction = instruction;
    
    const formData = {
        server_name: serverName,
        name: document.getElementById('serverName').value,
        description: document.getElementById('serverDescription').value,
        instruction: instruction,
        prompt: document.getElementById('serverPrompt').value
    };
    
    const resultContainer = document.getElementById('executeResult');
    resultContainer.innerHTML = '<div class="alert alert-info">서버 실행 중...</div>';
    
    try {
        const response = await fetch('/api/mcp-servers/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentRequestId = result.request_id;
            resultContainer.innerHTML = `
                <div class="alert alert-success">
                    <h6>실행 성공!</h6>
                    <div class="mb-2">
                        <strong>Request ID:</strong> <code>${result.request_id}</code>
                        <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${result.request_id}')">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>
                    <p>실행 결과는 위의 "최근 실행 결과" 섹션에서 확인하실 수 있습니다.</p>
                </div>
            `;
            
            // 실행 결과 영역 표시 및 메시지 숨김
            document.getElementById('currentExecutionResult').style.display = 'block';
            document.getElementById('noResultMessage').style.display = 'none';
            
            // 현재 실행 결과 로드 (1초 후)
            setTimeout(() => loadCurrentExecutionResults(instruction), 1000);
            
            // 전체 로그 새로고침
            loadServerLogs(1);
        } else {
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    서버 실행 실패: ${result.detail}
                </div>
            `;
        }
    } catch (error) {
        console.error('서버 실행 실패:', error);
        resultContainer.innerHTML = `
            <div class="alert alert-danger">
                서버 실행 중 오류가 발생했습니다.
            </div>
        `;
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

// 유틸리티 함수
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 페이지 초기 로드 시 최신 실행 결과 표시
async function loadInitialResults() {
    try {
        // 최신 MCP 서버 로그 확인
        const mcpResponse = await fetch(`/api/mcp-logs/paginated?server_name=${serverName}&page=1&per_page=1`);
        const mcpData = await mcpResponse.json();
        
        if (mcpData.logs.length > 0) {
            // 최신 로그가 있으면 실행 결과 영역 표시
            document.getElementById('currentExecutionResult').style.display = 'block';
            document.getElementById('noResultMessage').style.display = 'none';
            
            // 최신 MCP 결과 로드 - 같은 request_id를 가진 모든 로그
            const log = mcpData.logs[0];
            const request_id = log[9];
            
            if (request_id) {
                const allMcpResponse = await fetch(`/api/mcp-logs/by-request/${request_id}`);
                const allMcpLogs = await allMcpResponse.json();
                
                let mcpHtml = `<div class="mb-2">
                    <strong>Request ID:</strong> <code>${request_id}</code>
                    <button class="btn btn-sm btn-outline-secondary ms-2" onclick="copyToClipboard('${request_id}')">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>`;
                
                if (allMcpLogs.length > 1) {
                    // 여러 개의 MCP 로그가 있으면 accordion으로 표시
                    mcpHtml += '<div class="accordion" id="initialMcpAccordion">';
                    allMcpLogs.forEach((mcpLog, index) => {
                        mcpHtml += `
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="initialMcpHeading${index}">
                                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#initialMcpCollapse${index}">
                                        ${escapeHtml(mcpLog[2])} - ${new Date(mcpLog[7]).toLocaleString()}
                                    </button>
                                </h2>
                                <div id="initialMcpCollapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" data-bs-parent="#initialMcpAccordion">
                                    <div class="accordion-body">
                                        <p><strong>지시사항:</strong> ${escapeHtml(mcpLog[4])}</p>
                                        <div class="markdown-content">${parseMarkdown(mcpLog[6])}</div>
                                        <small class="text-muted">${new Date(mcpLog[7]).toLocaleString()}</small>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    mcpHtml += '</div>';
                } else {
                    // 하나의 로그만 있으면 단일 카드로 표시
                    const mcpLog = allMcpLogs[0];
                    mcpHtml += `
                        <div class="card">
                            <div class="card-body">
                                <h6 class="card-title">${escapeHtml(mcpLog[2])}</h6>
                                <p><strong>지시사항:</strong> ${escapeHtml(mcpLog[4])}</p>
                                <div class="markdown-content">${parseMarkdown(mcpLog[6])}</div>
                                <small class="text-muted">${new Date(mcpLog[7]).toLocaleString()}</small>
                            </div>
                        </div>
                    `;
                }
                
                document.getElementById('currentMcpResult').innerHTML = mcpHtml;
            } else {
                document.getElementById('currentMcpResult').innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${escapeHtml(log[2])}</h6>
                            <p><strong>지시사항:</strong> ${escapeHtml(log[4])}</p>
                            <div class="markdown-content">${parseMarkdown(log[6])}</div>
                            <small class="text-muted">${new Date(log[7]).toLocaleString()}</small>
                        </div>
                    </div>
                `;
            }
            
            // 최신 SQL Agent 로그 로드
            await loadLatestSqlAgentLogs();
        } else {
            // 실행 결과가 없으면 메시지 표시
            document.getElementById('currentExecutionResult').style.display = 'none';
            document.getElementById('noResultMessage').style.display = 'block';
        }
    } catch (error) {
        console.error('초기 결과 로드 실패:', error);
        document.getElementById('currentExecutionResult').style.display = 'none';
        document.getElementById('noResultMessage').style.display = 'block';
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('serverUpdateForm').addEventListener('submit', updateServerInfo);
    document.getElementById('serverExecuteForm').addEventListener('submit', executeServer);
    
    loadServerInfo();
    loadServerLogs(1);
    loadInitialResults(); // 초기 실행 결과 로드
}); 