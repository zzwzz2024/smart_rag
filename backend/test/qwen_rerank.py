import requests
import os

# 从环境变量中获取 API Key
api_key = ""

# 请求 URL
url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"

# 请求头
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 请求体
data = {
    "model": "gte-rerank-v2",
    # "model": "qwen3-rerank",
    "input": {
        "query": "什么是文本排序模型",
        "documents": [
            "文本排序模型广泛用于搜索引擎和推荐系统中，它们根据文本相关性对候选文本进行排序",
            "量子计算是计算科学的一个前沿领域",
            "预训练语言模型的发展给文本排序模型带来了新的进展"
        ]
    },
    "parameters": {
        "return_documents": True,
        "top_n": 5
    }
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)

# 输出响应结果
if response.status_code == 200:
    print("请求成功:")
    print(response.json())
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)
