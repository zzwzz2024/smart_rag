-- 知识库与标签的关联表
CREATE TABLE IF NOT EXISTS knowledge_base_tag_association (
    knowledge_base_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (knowledge_base_id, tag_id),
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
