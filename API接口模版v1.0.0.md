# API接口访问文档

## 1. 概述

本文档详细说明如何使用API授权码访问知识库，包括授权验证、知识库查询等功能的调用方法和参数说明。

## 2. 接口信息

### 2.1 接口说明

| 接口名称 | 方法 | 路径 | 功能描述 |
|---------|------|------|----------|
| 授权验证 | GET | /api/api-auth/validate/{auth_code} | 验证API授权码是否有效 |
| 知识库查询 | POST | /api/api-auth/chat | 使用授权码访问知识库并获取回答 |

### 2.2 授权内容
| 序号 | 授权厂商  | 授权码 | 知识库ID | 知识库名称  | 授权码有效期  | 
|------|------|------|------|------|
| 1 | 蓝点 | xxxxxxxxxxxxx |xxxxxxxxxxxxx | 法律法规检索 |2026-03-22至2026-03-23 |


## 3. 授权验证接口

### 3.1 接口说明

验证API授权码是否有效，并返回授权信息，包括授权的知识库列表。

### 3.2 请求参数

| 参数名 | 类型 | 位置    | 必填 | 描述     |
|--------|------|-------|----|--------|
| auth_code | string | 路径    | 是  | API授权码 |
| expires_at | string | 授权有效期 | 是  | 授权码有效期 |

### 3.3 响应格式

```json
{
  "success": true,
  "data": {
    "valid": true,
    "message": "授权有效",
    "authorization": {
      "vendor_name": "供应商名称",
      "knowledge_bases": [
        {
          "id": "知识库ID",
          "name": "知识库名称"
        }
      ],
      "expires_at": "2026-03-22T13:07:01.394000"
    }
  },
  "message": ""
}
```

### 3.4 调用示例

```bash
# 使用curl调用
curl "http://localhost:8000/api/api-auth/validate/your_auth_code"

# 带IP参数
curl "http://localhost:8000/api/api-auth/validate/your_auth_code?ip=192.168.1.100"
```

## 4. 知识库查询接口

### 4.1 接口说明

使用API授权码访问指定知识库，发送查询并获取回答。

### 4.2 请求参数

| 参数名 | 类型 | 位置 | 必填 | 描述 |
|--------|------|------|------|------|
| auth_code | string | 查询 | 是 | API授权码 |
| query | string | 请求体 | 是 | 查询问题 |
| kb_id | string | 请求体 | 是 | 知识库ID |
| model_id | string | 请求体 | 否 | 模型ID（可选，默认使用知识库配置的模型） |

### 4.3 请求体示例

```json
{
  "query": "什么是机器学习？",
  "kb_id": "69701332-85a5-431b-ab16-495b84b6f348",
  "model_id": "model_123"
}
```

### 4.4 响应格式

```json
{
  "success": true,
  "data": {
    "success": true,
    "answer": "{\"filename\": \"2.txt\", \"content\": \"你好，你是谁？\\r我是林俊杰\\r最近写了一首新歌\", \"score\": 0.016393442622950817}",
  },
  "message": ""
}
```

### 4.5 调用示例

```bash
# 使用curl调用
curl -X POST "http://localhost:8000/api/api-auth/chat?auth_code=your_auth_code" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是机器学习？",
    "kb_id": "69701332-85a5-431b-ab16-495b84b6f348"
  }'
```

## 5. 错误码说明

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数是否完整且格式正确 |
| 401 | 授权无效或已过期 | 检查授权码是否正确且在有效期内 |
| 403 | 知识库未授权 | 确保知识库在授权范围内 |
| 500 | 服务器内部错误 | 联系系统管理员 |

## 6. 完整调用流程

### 6.1 验证授权

在正式调用知识库查询接口前，建议先调用授权验证接口确认授权是否有效。

### 6.2 调用知识库查询

使用有效的授权码调用知识库查询接口，获取知识库的回答。

## 7. 示例代码

### 7.1 Python示例

```python
import requests
import json

# 授权验证
def validate_authorization(auth_code):
    url = f"http://localhost:8000/api/api-auth/validate/{auth_code}"
    response = requests.get(url)
    return response.json()

# 知识库查询
def query_knowledge_base(auth_code, query, kb_id, model_id=None):
    url = f"http://localhost:8000/api/api-auth/chat?auth_code={auth_code}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "kb_id": kb_id,
        "model_id": model_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# 使用示例
auth_code = "your_auth_code"
kb_id = "69701332-85a5-431b-ab16-495b84b6f348"

# 验证授权
validation_result = validate_authorization(auth_code)
if validation_result['data']['valid']:
    print("授权有效，可以查询知识库")
    # 查询知识库
    result = query_knowledge_base(
        auth_code, 
        "什么是机器学习？", 
        kb_id
    )
    print("回答:", result['data']['answer'])
else:
    print("授权无效:", validation_result['data']['message'])
```

### 7.2 工具调用

body选择raw格式，传参
{
    "query":"林俊杰最近写歌了吗",
    "kb_id":"69701332-85a5-431b-ab16-495b84b6f348"
}

返回数据
{
	"code": 200,
	"msg": "success",
	"data": {
		"success": true,
		"answer": "{\"filename\": \"2.txt\", \"content\": \"你好，你是谁？\\r我是林俊杰\\r最近写了一首新歌\", \"score\": 0.016393442622950817}"
	}
}


## 8. 注意事项

1. **授权码安全**：API授权码是访问知识库的重要凭证，请妥善保管，避免泄露。

2. **IP限制**：如果在创建授权时设置了IP白名单，只有指定IP的请求才能通过验证。

3. **有效期**：授权码有一定的有效期，过期后需要重新创建授权。

4. **知识库权限**：每个授权码只能访问指定的知识库，无法访问未授权的知识库。

5. **请求频率**：为了系统稳定，建议合理控制请求频率，避免过度调用。

6. **错误处理**：在调用接口时，应妥善处理各种错误情况，确保系统稳定性。

## 9. 故障排查

### 9.1 授权验证失败

- 检查授权码是否正确
- 检查授权是否在有效期内
- 检查客户端IP是否在白名单内

### 9.2 知识库查询失败

- 检查授权码是否有效
- 检查知识库ID是否正确且在授权范围内
- 检查模型是否可用
- 检查网络连接是否正常

## 10. 联系支持

如果在使用API接口过程中遇到问题，请联系系统管理员小王 xxx获取支持。

---

**文档版本**：1.0.0
**更新时间**：2026-02-20
