import os

# 定义项目根目录
project_root = "zzwzz_rag"

# 定义后端结构
backend_structure = {
    "app": {
        "__init__.py": "",
        "main.py": "# FastAPI 入口",
        "config.py": "# 配置管理",
        "database.py": "# 数据库连接",
        "models": {
            "__init__.py": "",
            "user.py": "",
            "knowledge_base.py": "",
            "document.py": "",
            "conversation.py": ""
        },
        "schemas": {
            "__init__.py": "",
            "user.py": "",
            "knowledge_base.py": "",
            "document.py": "",
            "chat.py": "",
            "evaluation.py": ""
        },
        "api": {
            "__init__.py": "",
            "router.py": "",
            "auth.py": "",
            "knowledge_base.py": "",
            "document.py": "",
            "chat.py": "",
            "evaluation.py": ""
        },
        "core": {
            "__init__.py": "",
            "document_parser.py": "# 文档解析",
            "chunker.py": "# 智能分块",
            "embedder.py": "# 向量化",
            "vector_store.py": "# 向量存储",
            "retriever.py": "# 混合检索",
            "reranker.py": "# 重排序",
            "generator.py": "# LLM 生成",
            "rag_pipeline.py": "# RAG 编排",
            "evaluator.py": "# 效果评估"
        },
        "services": {
            "__init__.py": "",
            "kb_service.py": "",
            "doc_service.py": "",
            "chat_service.py": ""
        },
        "utils": {
            "__init__.py": "",
            "auth.py": "",
            "file_utils.py": ""
        }
    },
    "uploads": {},
    "requirements.txt": "",
    "Dockerfile": "",
    "docker-compose.yml": "",
    "alembic.ini": ""
}

# 定义前端结构
frontend_structure = {
    "public": {},
    "src": {
        "main.ts": "",
        "App.vue": "",
        "router": {
            "index.ts": ""
        },
        "stores": {
            "app.ts": "",
            "chat.ts": "",
            "kb.ts": "",
            "user.ts": ""
        },
        "api": {
            "request.ts": "",
            "auth.ts": "",
            "kb.ts": "",
            "document.ts": "",
            "chat.ts": "",
            "evaluation.ts": ""
        },
        "views": {
            "Login.vue": "",
            "Layout.vue": "",
            "Chat.vue": "",
            "KnowledgeBase.vue": "",
            "Documents.vue": "",
            "Evaluation.vue": "",
            "Settings.vue": ""
        },
        "components": {
            "ChatMessage.vue": "",
            "FileUpload.vue": "",
            "KBCard.vue": "",
            "DocList.vue": "",
            "CitationPanel.vue": "",
            "ConfidenceBadge.vue": ""
        },
        "types": {
            "index.ts": ""
        },
        "styles": {
            "main.scss": ""
        }
    },
    "index.html": "",
    "package.json": "",
    "tsconfig.json": "",
    "vite.config.ts": "",
    "env.d.ts": ""
}

# 创建文件夹和文件的函数
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # 如果是字典，表示这是一个文件夹
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # 如果不是字典，表示这是一个文件
            with open(path, "w") as f:
                f.write(content)

# 创建整个项目结构
if __name__ == "__main__":
    # 创建后端结构
    backend_path = os.path.join(project_root, "backend")
    os.makedirs(backend_path, exist_ok=True)
    create_structure(backend_path, backend_structure)

    # 创建前端结构
    frontend_path = os.path.join(project_root, "frontend")
    os.makedirs(frontend_path, exist_ok=True)
    create_structure(frontend_path, frontend_structure)

    # 创建 README.md
    readme_path = os.path.join(project_root, "README.md")
    with open(readme_path, "w") as f:
        f.write("# SmartRAG Project\n\nThis is the SmartRAG project.")

    print("Project structure created successfully!")
