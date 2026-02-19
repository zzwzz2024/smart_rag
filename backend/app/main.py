# main.py
from fastapi import FastAPI
import uvicorn
from backend.app.api.router import api_router  # 引入已定义的路由
from backend.app.database import init_db  # 引入数据库初始化函数
# 创建 FastAPI 应用实例
app = FastAPI()

# 注册所有 API 路由
app.include_router(api_router)

# 根路径示例（可选）
@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartRAG Backend!"}

# 启动事件：初始化数据库
@app.on_event("startup")
async def startup_event():
    await init_db()

# 可选：内嵌启动逻辑
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)