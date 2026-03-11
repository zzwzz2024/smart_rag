-- 知识库与领域的关联表
CREATE TABLE IF NOT EXISTS knowledge_base_domain_association (
    knowledge_base_id VARCHAR(36) NOT NULL,
    domain_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (knowledge_base_id, domain_id),
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
);
