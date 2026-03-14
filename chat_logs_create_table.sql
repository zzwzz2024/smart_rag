-- 创建chat_logs表
CREATE TABLE IF NOT EXISTS chat_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    conversation_id VARCHAR(36) REFERENCES conversations(id),
    message_id VARCHAR(36) REFERENCES messages(id),
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_used VARCHAR(100),
    knowledge_bases JSONB,
    response_time FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON chat_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_logs_user_id ON chat_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_conversation_id ON chat_logs(conversation_id);