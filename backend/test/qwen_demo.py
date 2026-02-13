from openai import OpenAI
from backend.app.config import get_settings

setting = get_settings()
print(f"OPENAI_API_KEY: {setting.OPENAI_API_KEY}")
print(f"OPENAI_BASE_URL: {setting.OPENAI_BASE_URL}")

api_key = setting.OPENAI_API_KEY
base_url = setting.OPENAI_BASE_URL

client = OpenAI(
    api_key= api_key.strip(),
    base_url= base_url.strip()
)

# client = OpenAI(
#     api_key= "sk-f7758e4555e045fdb02d12579fee29b5",
#     base_url= "https://dashscope.aliyuncs.com/compatible-mode/v1"
# )

try:
    # 尝试调用一个简单的补全接口测试
    response = client.chat.completions.create(
        model="qwen3-max",
        messages=[{"role": "user", "content": "你好"}]
    )
    print("连接成功:", response)
except Exception as e:
    print("连接失败:", e)