-- 创建模型厂商表
CREATE TABLE IF NOT EXISTS model_vendors (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_model_vendors_name ON model_vendors(name);

-- 插入常用模型厂商数据
INSERT INTO model_vendors (id, name, description) VALUES
('openai', 'OpenAI', 'OpenAI是人工智能研究实验室，开发了GPT系列模型'),
('qwen', 'Qwen', 'Qwen是阿里云开发的开源大语言模型'),
('deepseek', 'DeepSeek', 'DeepSeek是深度求索开发的大语言模型'),
('ollama', 'Ollama', 'Ollama是一个本地运行大语言模型的工具'),
('anthropic', 'Anthropic', 'Anthropic开发了Claude系列模型'),
('google', 'Google', 'Google开发了Gemini系列模型'),
('microsoft', 'Microsoft', 'Microsoft开发了Phi系列模型'),
('meta', 'Meta', 'Meta开发了Llama系列开源模型')
ON CONFLICT (name) DO NOTHING;

-- 更新时间戳触发器（可选）
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_model_vendors_timestamp
BEFORE UPDATE ON model_vendors
FOR EACH ROW
EXECUTE PROCEDURE update_timestamp();
