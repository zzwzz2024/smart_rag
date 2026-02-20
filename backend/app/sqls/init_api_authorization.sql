-- 1. 创建更新时间戳的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- 2. 修改表定义（去掉 ON UPDATE）
CREATE TABLE IF NOT EXISTS api_authorizations (
    id VARCHAR(36) PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_contact VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    authorized_ips TEXT,
    auth_code VARCHAR(64) NOT NULL UNIQUE,
    start_time TIMESTAMPTZ NOT NULL,      -- 建议用 TIMESTAMPTZ（带时区）
    end_time TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(), -- 使用 NOW() 替代 CURRENT_TIMESTAMP
    updated_at TIMESTAMPTZ DEFAULT NOW()  -- 初始值设为 NOW()
);

-- 3. 为 api_authorizations 表创建触发器
CREATE TRIGGER update_api_authorizations_updated_at
   BEFORE UPDATE ON api_authorizations
   FOR EACH ROW
   EXECUTE FUNCTION update_updated_at_column();                        ^

-- 创建知识库授权关联表
CREATE TABLE IF NOT EXISTS knowledge_base_authorization_association (
    authorization_id VARCHAR(36) NOT NULL,
    knowledge_base_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (authorization_id, knowledge_base_id),
    FOREIGN KEY (authorization_id) REFERENCES api_authorizations(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_api_authorizations_vendor_name ON api_authorizations(vendor_name);
CREATE INDEX IF NOT EXISTS idx_api_authorizations_auth_code ON api_authorizations(auth_code);
CREATE INDEX IF NOT EXISTS idx_api_authorizations_is_active ON api_authorizations(is_active);
CREATE INDEX IF NOT EXISTS idx_api_authorizations_end_time ON api_authorizations(end_time);
