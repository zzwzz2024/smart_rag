# main.py
from fastapi import FastAPI
from backend.app.api.router import api_router  # 引入已定义的路由
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI()

# 注册所有 API 路由
app.include_router(api_router)

# 根路径示例（可选）
@app.get("/")
def read_root():
    return {"message": "Welcome to the SmartRAG Backend!"}

# 可选：内嵌启动逻辑
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)