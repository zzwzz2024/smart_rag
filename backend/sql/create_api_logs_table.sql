-- 创建API访问日志表
CREATE TABLE IF NOT EXISTS api_logs (
    id VARCHAR(36) PRIMARY KEY,
    auth_code VARCHAR(64) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    ip VARCHAR(50) NOT NULL,
    user_agent TEXT,
    status INTEGER NOT NULL,
    response_time INTEGER NOT NULL, -- 响应时间（毫秒）
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_api_logs_auth_code ON api_logs(auth_code);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);