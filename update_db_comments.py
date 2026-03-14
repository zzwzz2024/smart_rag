"""
根据 schemas 文件夹中的字段注释，更新数据库表的字段注释
"""
import os
import re
import sys
import importlib.util
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 在导入其他模块前，先检查 psycopg2
print("=" * 60)
print("检查依赖和连接...")
print("=" * 60)

try:
    import psycopg2
    print(f"✓ psycopg2 已安装，版本：{psycopg2.__version__}")
except ImportError as e:
    print(f"✗ psycopg2 未安装")
    print(f"  错误信息：{e}")
    print("\n请运行以下命令安装:")
    print("  pip install psycopg2-binary")
    sys.exit(1)

# 测试直接连接
try:
    print("\n测试 PostgreSQL 直接连接...")
    test_conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="rag",
        user="postgres",
        password="P@ssw0rd"
    )
    test_cursor = test_conn.cursor()
    test_cursor.execute("SELECT version();")
    db_version = test_cursor.fetchone()[0]
    print(f"✓ PostgreSQL 连接成功!")
    print(f"  数据库版本：{db_version[:50]}...")
    test_cursor.close()
    test_conn.close()
except Exception as e:
    print(f"✗ PostgreSQL 连接失败")
    print(f"  错误信息：{e}")
    print("\n可能的原因:")
    print("  1. PostgreSQL 服务未启动")
    print("  2. 数据库 'rag' 不存在")
    print("  3. 用户名或密码错误")
    print("  4. 端口 5432 被占用或防火墙阻止")
    sys.exit(1)

# 测试 SQLAlchemy 连接
try:
    print("\n测试 SQLAlchemy 连接...")
    # 直接使用已验证的连接参数创建引擎
    from sqlalchemy import create_engine, text

    # 使用与 psycopg2 直连相同的密码
    DATABASE_URL_TEST = "postgresql://postgres:P%40ssw0rd@localhost:5432/rag"
    test_engine = create_engine(DATABASE_URL_TEST)

    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1;"))
        print(f"✓ SQLAlchemy 连接成功!")

    test_engine.dispose()

except ImportError:
    print("  提示：不需要安装 sqlalchemy-utils")
except Exception as e:
    print(f"✗ SQLAlchemy 连接测试失败")
    print(f"  错误信息：{e}")
    print("\n尝试使用默认密码 'postgres'...")

    # 尝试使用默认密码
    try:
        DATABASE_URL_TEST2 = "postgresql://postgres:postgres@localhost:5432/rag"
        test_engine2 = create_engine(DATABASE_URL_TEST2)

        with test_engine2.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            print(f"✓ 使用默认密码 'postgres' 连接成功!")

        test_engine2.dispose()
    except Exception as e2:
        print(f"✗ 使用默认密码也失败：{e2}")
        sys.exit(1)

print("=" * 60)
print("")

# 数据库连接信息 - 使用正确的密码
DATABASE_URL = "postgresql://postgres:P%40ssw0rd@localhost:5432/rag"

# 创建数据库引擎，echo=True 显示执行的 SQL
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 表名映射
TABLE_MAPPING = {
    "User": "sys_users",
    "KnowledgeBase": "kb_knowledge_bases",
    "Document": "kb_documents",
    "DocumentChunk": "kb_document_chunks",
    "Conversation": "chat_conversations",
    "Message": "chat_messages",
    "Feedback": "chat_feedbacks",
    "ChatLog": "chat_logs",
    "ModelVendor": "m_model_vendors",
    "Model": "m_models",
    "Role": "sys_roles",
    "Menu": "sys_menus",
    "Permission": "sys_permissions",
    "Dictionary": "sys_dictionaries",
    "DictionaryItem": "sys_dictionary_items"
}

# 字段映射（处理 schema 字段名与数据库字段名的差异）
# 字段映射（处理 schema 字段名与数据库字段名的差异）
FIELD_MAPPING = {
    "password": "hashed_password",  # User 模型中的 hashed_password 对应 schema 中的 password
}

# 默认字段注释（当 schema 中没有定义时使用）
DEFAULT_FIELD_COMMENTS = {
    # 通用字段
    "id": "主键 ID",
    "created_at": "创建时间",
    "updated_at": "更新时间",
    "is_deleted": "是否删除",

    # API 日志相关
    "auth_code": "授权码",
    "endpoint": "API 端点",
    "method": "HTTP 方法",
    "ip": "请求 IP 地址",
    "user_agent": "用户代理",
    "status": "响应状态码",
    "response_time": "响应时间（毫秒）",
    "error_message": "错误消息",

    # 用户相关
    "username": "用户名",
    "email": "邮箱地址",
    "hashed_password": "加密密码",
    "is_active": "是否激活",
    "role": "角色",
    "role_id": "角色 ID",

    # 知识库相关
    "name": "名称",
    "description": "描述",
    "avatar": "头像/图标",
    "embedding_model": "嵌入模型",
    "embedding_model_id": "嵌入模型 ID",
    "rerank_model": "重排序模型",
    "rerank_model_id": "重排序模型 ID",
    "chunk_size": "分块大小",
    "chunk_overlap": "分块重叠大小",
    "chunk_method": "分块方法",
    "retrieval_mode": "检索模式",
    "doc_count": "文档数量",
    "chunk_count": "分块数量",
    "owner_id": "所有者 ID",

    # 文档相关
    "filename": "文件名",
    "file_path": "文件路径",
    "file_type": "文件类型",
    "file_size": "文件大小（字节）",
    "kb_id": "知识库 ID",
    "doc_id": "文档 ID",
    "status": "处理状态",
    "chunk_count": "分块数量",
    "error_msg": "错误消息",
    "meta": "元数据",

    # 分块相关
    "content": "文本内容",
    "chunk_index": "分块索引",
    "token_count": "Token 数量",

    # 对话相关
    "user_id": "用户 ID",
    "title": "标题",
    "pinned": "是否置顶",
    "conversation_id": "对话 ID",
    "message_id": "消息 ID",
    "role": "角色",
    "citations": "引用",
    "confidence": "置信度",
    "retrieval_info": "检索信息",
    "token_usage": "Token 使用情况",
    "query": "查询内容",
    "answer": "回答内容",
    "model_used": "使用的模型",
    "knowledge_bases": "使用的知识库",

    # 反馈相关
    "rating": "评分",
    "comment": "评论",

    # 领域相关
    "is_active": "是否激活",
    "color": "颜色",

    # 权限相关
    "code": "编码",
    "menu_id": "菜单 ID",
    "permission_id": "权限 ID",
    "permission_ids": "权限 ID 列表",

    # 字典相关
    "type": "类型",
    "key": "键",
    "value": "值",
    "label": "标签",
    "sort": "排序",
    "dictionary_id": "字典 ID",

    # 模型相关
    "model": "模型标识",
    "vendor_id": "厂商 ID",
    "vendor_name": "厂商名称",
    "api_key": "API 密钥",
    "base_url": "基础 URL",
    "is_default": "是否默认",
    "top_k": "Top K 值",
    "temperature": "温度参数",
    "top_p": "Top P 值",

    # 菜单相关
    "parent_id": "父菜单 ID",
    "path": "路径",
    "icon": "图标",

    # 授权相关
    "vendor_contact": "供应商联系人",
    "contact_phone": "联系电话",
    "authorized_ips": "授权 IP 列表",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "knowledge_base_ids": "知识库 ID 列表",

    # 评估相关
    "reference_answer": "参考答案",
    "rag_answer": "RAG 回答",
    "score": "分数",

    #通用字段
    "created_at":"创建时间",
    "updated_at":"创建时间",
    "is_deleted":"创建时间",
}


def get_schema_fields(schema_path):
    """
    从 schema 文件中提取字段及其描述
    """
    fields = {}
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # 模式 1: 匹配 Field(..., description="...") 格式
        pattern1 = r'(\w+):\s*\w+\s*=\s*Field\([^)]*description\s*=\s*["\']([^"\']*)["\'][^)]*\)'
        matches1 = re.findall(pattern1, content, re.DOTALL)
        for field_name, description in matches1:
            fields[field_name] = description.strip()

        # 模式 2: 匹配带 Optional 的字段
        pattern2 = r'(\w+):\s*Optional\[\w+\]\s*=\s*Field\([^)]*description\s*=\s*["\']([^"\']*)["\'][^)]*\)'
        matches2 = re.findall(pattern2, content, re.DOTALL)
        for field_name, description in matches2:
            if field_name not in fields:
                fields[field_name] = description.strip()

        # 模式 3: 匹配多行的 Field 定义
        pattern3 = r'(\w+):\s*(?:Optional\[\w+\]|\w+)\s*=\s*Field\((.*?)description\s*=\s*["\']([^"\']*)["\'](.*?)\)'
        matches3 = re.findall(pattern3, content, re.DOTALL)
        for match in matches3:
            field_name = match[0]
            description = match[2].strip()
            if field_name not in fields:
                fields[field_name] = description

    return fields

def get_model_fields(model_path):
    """
    从模型文件中提取表名和字段名
    """
    tables = {}
    current_class = None
    current_table = None
    current_fields = []

    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # 查找所有类定义
        class_pattern = r'class\s+(\w+)\(Base\):'
        class_matches = re.finditer(class_pattern, content)

        classes = list(class_matches)
        for i, class_match in enumerate(classes):
            class_name = class_match.group(1)
            start_pos = class_match.end()
            end_pos = classes[i + 1].start() if i < len(classes) - 1 else len(content)
            class_content = content[start_pos:end_pos]

            # 查找表名
            table_match = re.search(r'__tablename__\s*=\s*["\']([^"\']*)["\']', class_content)
            table_name = table_match.group(1) if table_match else None

            # 查找字段 - 改进正则表达式以匹配多行
            field_pattern = r'(\w+):\s*Mapped\s*\[.*?\]\s*=\s*mapped_column\('
            field_matches = re.finditer(field_pattern, class_content, re.DOTALL)
            fields = [m.group(1) for m in field_matches]

            tables[class_name] = {
                "table_name": table_name,
                "fields": fields
            }

    return tables

def generate_alter_scripts(schema_fields, model_tables):
    """
    生成修改字段注释的 SQL 脚本
    """
    scripts = []

    # 遍历每个模型的表
    for class_name, table_info in model_tables.items():
        table_name = table_info["table_name"]
        model_fields = table_info["fields"]

        print(f"处理表 {table_name} ({class_name}), 字段数：{len(model_fields)}")

        # 遍历模型的每个字段
        for model_field in model_fields:
            # 跳过一些特殊字段
            # if model_field in ['id']:
            #     continue

            # 找到对应的 schema 字段名
            schema_field_name = None

            # 检查是否有反向映射（model -> schema）
            for schema_f, model_f in FIELD_MAPPING.items():
                if model_f == model_field:
                    schema_field_name = schema_f
                    break

            if not schema_field_name:
                schema_field_name = model_field

            # 在 schema 字段中查找
            if schema_field_name in ['id']:
                script = f"COMMENT ON COLUMN {table_name}.{model_field} IS 'ID';"
                scripts.append(script)
            elif schema_field_name in schema_fields:
                description = schema_fields[schema_field_name]
                script = f"COMMENT ON COLUMN {table_name}.{model_field} IS '{description}';"
                scripts.append(script)
                print(f"  ✓ {model_field} <- {schema_field_name}: {description}")
            elif model_field in DEFAULT_FIELD_COMMENTS:
                # 使用默认注释
                description = DEFAULT_FIELD_COMMENTS[model_field]
                script = f"COMMENT ON COLUMN {table_name}.{model_field} IS '{description}';"
                scripts.append(script)
                print(f"  ✓ {model_field} <- [默认]: {description}")
            else:
                print(f"  ✗ {model_field} (未找到 schema 注释)")

    return scripts

def execute_scripts(scripts):
    """
    执行 SQL 脚本
    """
    print(f"\n开始执行 {len(scripts)} 个 SQL 脚本...\n")

    db = SessionLocal()
    success_count = 0
    error_count = 0
    failed_scripts = []

    try:
        # 先测试连接是否有效
        print("测试数据库连接...")
        test_result = db.execute(text("SELECT 1;"))
        print(f"✓ 数据库连接正常\n")

        for i, script in enumerate(scripts, 1):
            try:
                print(f"[{i}/{len(scripts)}] 执行：{script}")

                # 使用文本模式执行
                result = db.execute(text(script))
                success_count += 1
                print(f"       ✓ 成功 (影响行数：{result.rowcount})")

            except Exception as e:
                error_msg = type(e).__name__
                full_error = str(e)

                # 获取原始的错误信息
                if hasattr(e, 'orig'):
                    orig_error = str(e.orig)
                    full_error = f"{full_error}\n原始错误：{orig_error}"

                error_detail = str(e.__cause__) if e.__cause__ else ""
                error_count += 1

                print(f"       ✗ 失败")
                print(f"          错误类型：{error_msg}")
                print(f"          完整错误：{full_error[:300]}")
                if error_detail:
                    print(f"          详情：{error_detail[:300]}")

                failed_scripts.append((script, full_error))

                # 如果是连接错误，尝试重新连接
                if "OperationalError" in error_msg or "connection" in full_error.lower():
                    print("\n检测到连接问题，尝试重新连接...")
                    try:
                        db.close()
                        db = SessionLocal()
                        print("✓ 重新连接成功\n")
                    except Exception as reconnect_error:
                        print(f"✗ 重新连接失败：{reconnect_error}\n")

        # 提交结果
        if success_count > 0:
            print(f"\n正在提交 {success_count} 个成功的更改...")
            try:
                db.commit()
                print(f"✓ 提交成功!")
            except Exception as commit_error:
                print(f"✗ 提交失败：{commit_error}")
                print("正在回滚...")
                db.rollback()
        else:
            print("\n没有成功的更改，执行回滚...")
            db.rollback()

        # 显示统计
        print("\n" + "=" * 60)
        print(f"执行统计:")
        print(f"  总脚本数：{len(scripts)}")
        print(f"  成功：{success_count}")
        print(f"  失败：{error_count}")
        print("=" * 60)

        # 显示失败的脚本详情
        if failed_scripts:
            print(f"\n失败的脚本详情 (前 5 个):")
            for i, (script, error) in enumerate(failed_scripts[:5], 1):
                print(f"\n{i}. 脚本：{script}")
                print(f"   错误：{error}")

    except Exception as e:
        print(f"\n执行过程中发生严重错误：{e}")
        import traceback
        traceback.print_exc()
        print("正在回滚所有更改...")
        db.rollback()
    finally:
        db.close()
        print("\n数据库连接已关闭")

def main():
    """
    主函数
    """
    # 1. 读取所有 schema 文件
    schema_dir = "backend/app/schemas"
    all_schema_fields = {}

    print("=== 读取 Schema 文件 ===")
    for filename in os.listdir(schema_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            schema_path = os.path.join(schema_dir, filename)
            fields = get_schema_fields(schema_path)
            if fields:
                print(f"{filename}: 找到 {len(fields)} 个字段")
                all_schema_fields.update(fields)

    print(f"\n总共收集到 {len(all_schema_fields)} 个 schema 字段")

    # 2. 读取所有模型文件
    model_dir = "backend/app/models"
    all_model_tables = {}

    print("\n=== 读取 Model 文件 ===")
    for filename in os.listdir(model_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            model_path = os.path.join(model_dir, filename)
            tables = get_model_fields(model_path)
            if tables:
                print(f"{filename}: 找到 {len(tables)} 个表")
                for table_name, info in tables.items():
                    print(f"  - {table_name}: {info['table_name']} ({len(info['fields'])} 字段)")
                all_model_tables.update(tables)

    print(f"\n总共收集到 {len(all_model_tables)} 个模型类")

    # 3. 生成 SQL 脚本
    print("\n=== 生成 SQL 脚本 ===")
    scripts = generate_alter_scripts(all_schema_fields, all_model_tables)
    # print(scripts)

    # 4. 执行脚本
    if scripts:
        print(f"\n生成了 {len(scripts)} 个修改字段注释的脚本")
        execute_scripts(scripts)
    else:
        print("\n没有生成任何脚本")
        print("\n可能的原因:")
        print("1. Schema 字段和 Model 字段名称不匹配")
        print("2. 需要检查 FIELD_MAPPING 是否正确")
        print(f"3. Schema 字段列表：{list(all_schema_fields.keys())[:10]}...")

if __name__ == "__main__":
    main()
