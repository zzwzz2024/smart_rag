-- 创建数据库
-- CREATE DATABASE model_manager;

-- 模型厂商表
CREATE TABLE IF NOT EXISTS model_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(100) NOT NULL,
    icon VARCHAR(50) DEFAULT '🤖',
    default_base_url VARCHAR(500),
    supported_models JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 模型配置表
CREATE TABLE IF NOT EXISTS model_configs (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES model_providers(id) ON DELETE CASCADE,
    model_name VARCHAR(200) NOT NULL,
    alias VARCHAR(200),
    api_key VARCHAR(1000) NOT NULL,
    base_url VARCHAR(500),

    -- 超参数
    temperature DOUBLE PRECISION DEFAULT 0.7,
    top_p DOUBLE PRECISION DEFAULT 1.0,
    max_tokens INTEGER DEFAULT 2048,
    frequency_penalty DOUBLE PRECISION DEFAULT 0.0,
    presence_penalty DOUBLE PRECISION DEFAULT 0.0,
    stop_sequences JSONB DEFAULT '[]'::jsonb,

    -- 状态
    is_active BOOLEAN DEFAULT true,
    description TEXT DEFAULT '',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_model_configs_provider ON model_configs(provider_id);
CREATE INDEX IF NOT EXISTS idx_model_configs_active ON model_configs(is_active);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_model_providers_updated_at
    BEFORE UPDATE ON model_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_configs_updated_at
    BEFORE UPDATE ON model_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认厂商数据
INSERT INTO model_providers (name, label, icon, default_base_url, supported_models) VALUES
('openai', 'OpenAI', '🟢', 'https://api.openai.com/v1',
 '["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1-preview", "o1-mini"]'::jsonb),

('anthropic', 'Anthropic', '🟤', 'https://api.anthropic.com',
 '["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"]'::jsonb),

('deepseek', 'DeepSeek', '🔵', 'https://api.deepseek.com/v1',
 '["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]'::jsonb),

('zhipu', '智谱AI', '🟣', 'https://open.bigmodel.cn/api/paas/v4',
 '["glm-4-plus", "glm-4", "glm-4-flash", "glm-4-long"]'::jsonb),

('qwen', '通义千问', '🟠', 'https://dashscope.aliyuncs.com/compatible-mode/v1',
 '["qwen-max", "qwen-plus", "qwen-turbo", "qwen-long"]'::jsonb),

('moonshot', 'Moonshot', '🌙', 'https://api.moonshot.cn/v1',
 '["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]'::jsonb),

('baichuan', '百川AI', '🔴', 'https://api.baichuan-ai.com/v1',
 '["Baichuan4", "Baichuan3-Turbo", "Baichuan2-Turbo"]'::jsonb),

('ollama', 'Ollama (本地)', '🦙', 'http://localhost:11434/v1',
 '["llama3", "mistral", "codellama", "qwen2"]'::jsonb)

ON CONFLICT (name) DO NOTHING;