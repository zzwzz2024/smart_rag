-- 为conversations表添加is_deleted字段
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_conversations_is_deleted ON conversations(is_deleted);

-- 为messages表添加is_deleted字段
ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_messages_is_deleted ON messages(is_deleted);

-- 为feedbacks表添加is_deleted字段
ALTER TABLE feedbacks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_feedbacks_is_deleted ON feedbacks(is_deleted);

-- 为chat_logs表添加is_deleted字段
ALTER TABLE chat_logs ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_chat_logs_is_deleted ON chat_logs(is_deleted);

-- 为knowledge_bases表添加is_deleted字段
ALTER TABLE knowledge_bases ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_is_deleted ON knowledge_bases(is_deleted);

-- 为documents表添加is_deleted字段
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_documents_is_deleted ON documents(is_deleted);

-- 为document_chunks表添加is_deleted字段
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_document_chunks_is_deleted ON document_chunks(is_deleted);

-- 为users表添加is_deleted字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON users(is_deleted);

-- 为model_vendors表添加is_deleted字段
ALTER TABLE model_vendors ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_model_vendors_is_deleted ON model_vendors(is_deleted);

-- 为models表添加is_deleted字段
ALTER TABLE models ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_models_is_deleted ON models(is_deleted);

-- 为evaluations表添加is_deleted字段
ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_evaluations_is_deleted ON evaluations(is_deleted);

-- 为domains表添加is_deleted字段
ALTER TABLE kb_domains ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_domains_is_deleted ON kb_domains(is_deleted);

-- 为tags表添加is_deleted字段
ALTER TABLE kb_tags ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS idx_tags_is_deleted ON kb_tags(is_deleted);