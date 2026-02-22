# SmartRAG

智能RAG检索系统，集成知识库管理、文档处理、准确率评估、API接口管理等功能。

## 技术架构

### 后端
- **框架**：FastAPI
- **ORM**：SQLAlchemy
- **数据库**：PostgreSQL
- **核心功能**：
  - RAG检索与生成
  - 知识库管理
  - 文档处理与存储
  - 准确率评估系统
  - API接口管理
  - 日志系统
  - 模型管理

### 前端
- **框架**：Vue 3
- **状态管理**：Pinia
- **UI库**：Element Plus
- **构建工具**：Vite
- **核心功能**：
  - 响应式界面设计
  - 知识库管理
  - 文档上传与预览
  - 准确率评估配置与结果查看
  - API接口管理
  - 对话历史管理
  - 置信度显示与颜色区分
  - 标签页管理与刷新功能

## 核心功能

### 1. 知识库管理
- 创建、编辑、删除知识库
- 上传文档到指定知识库
- 支持多种文档格式
- 知识库设置，包括分块方式选择（智能、按行、按段落）

### 2. 文档管理
- 按文件名和创建日期筛选文档
- 支持分页查看（每页10条）
- 点击分块数量查看文档内容
- 文档上传状态提示
- 文档内容分页显示
- 文档分块数量显示

### 3. 准确率评估系统
- 创建评估方案并关联知识库
- 支持选择问题和答案进行评估
- 查看评估结果和详细报告
- 评估历史记录管理

### 4. RAG检索功能
- 基于知识库的智能问答
- 上下文感知的回答生成
- 引用来源文档
- 置信度显示与颜色区分（低：红色，中：橙色，高：绿色）
- 对话历史管理

### 5. API接口管理
- 创建和管理API授权
- API文档下载
- 接口访问日志查看
- 接口访问统计（按厂商和接口名）

### 6. 模型管理
- 管理Embedding模型
- 管理聊天模型
- 管理Rerank模型
- 设置默认模型

## 安装与设置

### 后端设置
1. 进入后端目录
   ```bash
   cd backend
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 启动后端服务
   ```bash
   python app/main.py
   ```

### 前端设置
1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 启动开发服务器
   ```bash
   npm run dev
   ```

## API文档

### 后端API端点

#### 文档管理
- `GET /document/list/{kb_id}` - 获取文档列表（支持过滤和分页）
  - 参数：
    - `kb_id`：知识库ID
    - `filename`：文件名过滤（可选）
    - `created_from`：创建日期起始（可选）
    - `created_to`：创建日期结束（可选）
    - `page`：页码（默认1）
    - `page_size`：每页条数（默认10）

#### 评估管理
- `POST /evaluation/create` - 创建评估方案
- `GET /evaluation/list` - 获取评估列表（支持过滤和分页）

#### API接口管理
- `GET /api-auth/authorization` - 获取授权列表
- `POST /api-auth/authorization` - 创建授权
- `DELETE /api-auth/authorization/{id}` - 删除授权
- `GET /api-auth/chat` - API聊天接口
- `GET /api-auth/doc/download/{id}` - 下载API文档
- `GET /api-auth/logs` - 获取接口访问日志
- `GET /api-auth/logs/stats` - 获取接口访问统计

## 使用示例

### 1. 上传文档到知识库
1. 登录系统
2. 进入「文档管理」页面
3. 选择目标知识库
4. 点击「上传文档」按钮
5. 选择本地文件并上传
6. 查看上传状态和结果

### 2. 创建评估方案
1. 进入「评估管理」页面
2. 点击「创建评估方案」按钮
3. 选择关联的知识库
4. 配置评估参数
5. 提交创建

### 3. 执行RAG检索
1. 进入「智能问答」页面
2. 选择目标知识库
3. 输入问题
4. 查看系统生成的回答、置信度和引用来源

### 4. 管理API接口
1. 进入「API接口管理」页面
2. 点击「创建授权」按钮
3. 配置授权信息
4. 查看授权列表和状态
5. 点击「查看日志」按钮查看接口访问日志
6. 点击「下载文档」按钮下载API文档

## UI功能与改进

### 1. 响应式设计
- 适配不同屏幕尺寸
- 优化移动端体验

### 2. 用户反馈
- 操作成功/失败的对话框提示
- 上传进度显示
- 错误信息的友好展示

### 3. 交互体验
- 下拉框选择知识库（支持长英文名称）
- 文档内容预览与分页显示
- 平滑的页面过渡效果
- 标签页管理与刷新功能
- 置信度显示与颜色区分
- 对话历史管理

### 4. 系统功能
- 知识库设置，包括分块方式选择
- 模型管理，支持多种模型类型
- API接口管理与日志查看
- 搜索参数调整，优化检索效果

## 项目结构

### 后端结构
```
backend/
├── app/
│   ├── api/            # API路由
│   │   ├── api_auth/    # API接口管理相关路由
│   │   ├── endpoints/    # API端点
│   │   └── router.py     # 路由注册
│   ├── core/           # 核心功能
│   │   ├── chunker.py     # 文档分块
│   │   ├── embedder.py    # 文本向量化
│   │   ├── generator.py   # 答案生成
│   │   ├── retriever.py   # 混合检索
│   │   └── vector_store.py # 向量存储
│   ├── models/         # 数据库模型
│   ├── schemas/        # 数据验证
│   ├── services/       # 业务逻辑
│   ├── utils/          # 工具函数
│   └── main.py         # 应用入口
├── uploads/            # 文件上传目录
├── chroma_data/        # ChromaDB持久化目录
└── requirements.txt    # 依赖文件
```

### 前端结构
```
frontend/
├── src/
│   ├── api/            # API调用
│   ├── components/     # 组件
│   ├── router/         # 路由配置
│   ├── stores/         # 状态管理
│   ├── types/          # 类型定义
│   ├── views/          # 页面
│   │   ├── Chat.vue       # 智能问答
│   │   ├── Documents.vue  # 文档管理
│   │   ├── KnowledgeBase.vue # 知识库管理
│   │   ├── ApiAuthorization.vue # API接口管理
│   │   └── ModelSettings.vue # 模型管理
│   └── main.ts         # 应用入口
├── package.json        # 项目配置
└── vite.config.ts      # Vite配置
```

## 技术栈

### 后端
- Python 3.9+
- FastAPI
- SQLAlchemy
- Pydantic
- ChromaDB

### 前端
- TypeScript
- Vue 3
- Pinia
- Element Plus
- Axios
- ECharts

## 未来规划

- [ ] 支持更多文档格式
- [ ] 优化RAG检索算法
- [ ] 添加用户权限管理
- [ ] 实现多语言支持
- [ ] 增加更多评估指标
- [ ] 优化系统性能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License