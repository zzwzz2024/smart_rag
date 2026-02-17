from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
from backend.app.database import get_db
from backend.app.models.model import Model, ModelType, ModelVendor
from backend.app.schemas.model import (
    ModelCreate, ModelUpdate, ModelResponse, ModelListResponse,
    ModelVendorCreate, ModelVendorUpdate, ModelVendorResponse, ModelVendorListResponse
)
from backend.app.utils.auth import get_current_user
from backend.app.models.user import User
import time

router = APIRouter()


import httpx

# 验证模型是否有效
async def validate_model(model_data: dict):
    """验证模型配置是否有效"""
    # 基本验证
    if not model_data.get('name'):
        raise HTTPException(status_code=400, detail="模型名称不能为空")
    if not model_data.get('model'):
        raise HTTPException(status_code=400, detail="模型标识不能为空")
    if not model_data.get('type'):
        raise HTTPException(status_code=400, detail="模型类型不能为空")
    
    # 根据模型类型进行特定验证
    model_type = model_data.get('type')
    api_key = model_data.get('api_key', '').strip()
    base_url = model_data.get('base_url', '').strip()
    
    # 对于需要API调用的模型，验证API Key和基础URL
    if model_type in ['chat', 'embedding', 'rerank']:
        # 如果提供了API Key，验证基础URL
        if api_key and not base_url:
            raise HTTPException(status_code=400, detail="提供API Key时必须同时提供基础URL")
        
        # 对于OpenAI模型，验证API Key格式
        if api_key and 'openai' in base_url.lower():
            if not api_key.startswith('sk-'):
                raise HTTPException(status_code=400, detail="OpenAI API Key格式不正确，应以'sk-'开头")
        
        # 如果提供了API Key和基础URL，测试API是否可访问
        if api_key and base_url:
            await test_model_api(model_type, api_key, base_url, model_data.get('model'))

async def test_model_api(
    model_type: str,
    api_key: str,
    base_url: str,
    model_name: str,
    provider_name: Optional[str] = None,  # 新增：厂商标识，用于区分认证方式
):
    """
    测试模型API配置是否正确可用

    Args:
        model_type: 模型类型 - chat / embedding / rerank
        api_key: API密钥
        base_url: 接口基础地址
        model_name: 模型名称
        provider_name: 厂商标识（openai / anthropic / deepseek / ollama 等）

    Returns:
        dict: {"success": bool, "message": str, "response_time_ms": float}
    """

    # ========== 1. 基础参数校验 ==========

    if not base_url or not base_url.strip():
        raise HTTPException(status_code=400, detail="Base URL 不能为空")

    base_url = base_url.strip().rstrip("/")

    if not base_url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Base URL 格式错误，必须以 'http://' 或 'https://' 开头"
        )

    if not model_name or not model_name.strip():
        raise HTTPException(status_code=400, detail="模型名称不能为空")

    if model_type not in ("chat", "embedding", "rerank"):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的模型类型: {model_type}，可选值: chat / embedding / rerank"
        )

    # Ollama 等本地部署可以不需要 API Key
    is_local = provider_name in ("ollama",) or "localhost" in base_url or "127.0.0.1" in base_url
    if not api_key and not is_local:
        raise HTTPException(status_code=400, detail="API Key 不能为空")

    # ========== 2. 构建请求头和请求体 ==========

    headers = {"Content-Type": "application/json"}
    url = ""
    payload = {}

    # ---------- 判断是否为 Anthropic（认证方式不同） ----------
    is_anthropic = (
        provider_name == "anthropic"
        or "anthropic" in base_url.lower()
    )

    if is_anthropic:
        # Anthropic 使用 x-api-key 认证
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"

        if model_type == "chat":
            url = f"{base_url}/v1/messages"
            payload = {
                "model": model_name,
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Hi"}],
            }
        elif model_type == "embedding":
            raise HTTPException(
                status_code=400,
                detail="Anthropic 暂不支持 Embedding 模型，请选择其他厂商"
            )
        elif model_type == "rerank":
            raise HTTPException(
                status_code=400,
                detail="Anthropic 暂不支持 Rerank 模型，请选择其他厂商"
            )
    else:
        # ---------- OpenAI 兼容格式（绝大多数厂商） ----------
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        if model_type == "chat":
            url = f"{base_url}/chat/completions"
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5,
                "stream": False,
            }

        elif model_type == "embedding":
            url = f"{base_url}/embeddings"
            payload = {
                "model": model_name,
                "input": "test connection",
            }

        elif model_type == "rerank":
            url = f"{base_url}/rerank"
            payload = {
                "model": model_name,
                "query": "test query",
                "documents": ["document one", "document two"],
                "top_n": 1,
            }

    # ========== 3. 发送测试请求 ==========

    try:
        start_time = time.time()

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
        ) as client:
            response = await client.post(url, headers=headers, json=payload)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # ========== 4. 解析响应结果 ==========

        if response.status_code == 200:
            # 额外验证响应体是否合法
            try:
                resp_json = response.json()
                _validate_response_body(model_type, resp_json, is_anthropic)
            except HTTPException:
                raise
            except Exception:
                pass  # 响应 200 但格式异常，仍视为连接成功

            return {
                "success": True,
                "message": "连接成功，模型配置有效",
                "response_time_ms": elapsed_ms,
            }

        # ---------- 处理各类错误状态码 ----------
        error_body = _safe_parse_error(response)

        if response.status_code == 401:
            raise HTTPException(
                status_code=400,
                detail=f"认证失败（401）：API Key 无效或已过期。{error_body}"
            )

        elif response.status_code == 403:
            raise HTTPException(
                status_code=400,
                detail=f"权限不足（403）：API Key 没有访问该模型的权限。{error_body}"
            )

        elif response.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"接口不存在（404）：请检查 Base URL 是否正确，"
                    f"或模型名称 '{model_name}' 不存在。{error_body}"
                )
            )

        elif response.status_code == 429:
            # 429 说明认证和模型都没问题，只是限流了，可以视为配置正确
            return {
                "success": True,
                "message": "配置有效（当前触发限流，但连接和认证正常）",
                "response_time_ms": elapsed_ms,
            }

        elif response.status_code >= 500:
            raise HTTPException(
                status_code=400,
                detail=f"服务端错误（{response.status_code}）：模型服务异常，请稍后重试。{error_body}"
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"请求失败（{response.status_code}）：{error_body}"
            )

    # ========== 5. 异常处理 ==========

    except HTTPException:
        raise

    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=400,
            detail=f"连接超时：无法连接到 {base_url}，请检查 Base URL 是否正确、网络是否可达"
        )

    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=400,
            detail="读取超时：服务端响应时间过长，但连接已建立，建议检查模型是否正常运行"
        )

    except httpx.ConnectError as e:
        error_str = str(e)
        if "Name or service not known" in error_str or "getaddrinfo failed" in error_str:
            raise HTTPException(
                status_code=400,
                detail=f"域名解析失败：无法解析 {base_url}，请检查 URL 是否拼写正确"
            )
        elif "Connection refused" in error_str:
            raise HTTPException(
                status_code=400,
                detail=f"连接被拒绝：{base_url} 服务未启动或端口不正确"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"连接失败：{error_str}"
            )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"请求异常：{str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"未知错误：{str(e)}"
        )


def _safe_parse_error(response: httpx.Response) -> str:
    """安全地从响应中提取错误信息"""
    try:
        body = response.json()
        # OpenAI 格式
        if "error" in body:
            err = body["error"]
            if isinstance(err, dict):
                return err.get("message", str(err))
            return str(err)
        # Anthropic 格式
        if "message" in body:
            return body["message"]
        return str(body)[:300]
    except Exception:
        text = response.text[:300] if response.text else ""
        return text


def _validate_response_body(model_type: str, resp: dict, is_anthropic: bool):
    """
    验证返回体结构是否符合预期，防止连到了错误的服务但恰好返回 200 的情况
    """
    if is_anthropic:
        # Anthropic 返回应包含 content
        if "content" not in resp and "type" not in resp:
            raise HTTPException(
                status_code=400,
                detail="响应格式异常：返回 200 但响应体不符合 Anthropic 格式，请检查 Base URL"
            )
        return

    if model_type == "chat":
        # OpenAI chat 格式应包含 choices
        if "choices" not in resp and "id" not in resp:
            raise HTTPException(
                status_code=400,
                detail="响应格式异常：返回 200 但不含 'choices'，请检查 Base URL 是否指向正确的 API"
            )

    elif model_type == "embedding":
        # 应包含 data
        if "data" not in resp:
            raise HTTPException(
                status_code=400,
                detail="响应格式异常：返回 200 但不含 'data'，请检查 Base URL 和模型名称"
            )

    elif model_type == "rerank":
        # 应包含 results
        if "results" not in resp:
            raise HTTPException(
                status_code=400,
                detail="响应格式异常：返回 200 但不含 'results'，请检查 Rerank 接口地址"
            )

@router.post("/", response_model=ModelResponse)
async def create_model(
    model_in: ModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新模型"""
    # 检查是否已存在同名同类型模型
    existing_model = await db.execute(
        select(Model).where(
            Model.name == model_in.name,
            Model.type == model_in.type
        )
    )
    if existing_model.scalar():
        raise HTTPException(status_code=400, detail="已存在同名同类型模型")

    # 创建新模型
    model_data = model_in.model_dump()
    # 确保type是字符串
    if isinstance(model_data.get('type'), ModelType):
        model_data['type'] = model_data['type'].value
    
    # 确保api_key和base_url字段有值，即使是空字符串
    model_data['api_key'] = model_data.get('api_key') or ''
    model_data['base_url'] = model_data.get('base_url') or ''
    model_data['description'] = model_data.get('description') or ''
    
    # 验证模型配置
    await validate_model(model_data)
    
    model = Model(
        id=str(uuid.uuid4()),
        **model_data
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


@router.get("/list", response_model=ModelListResponse)
async def list_models(
    type: Optional[ModelType] = Query(None, description="模型类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型列表"""
    # 构建查询，包含vendor信息
    from sqlalchemy.orm import joinedload
    query = select(Model).options(joinedload(Model.vendor_obj))
    if type:
        # 确保type是字符串
        type_value = type.value if isinstance(type, ModelType) else type
        query = query.where(Model.type == type_value)

    # 计算总数
    count_query = select(func.count(Model.id))
    if type:
        type_value = type.value if isinstance(type, ModelType) else type
        count_query = count_query.where(Model.type == type_value)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    query = query.order_by(Model.created_at.desc()).offset(offset).limit(page_size)
    # query = query.offset(offset).limit(page_size)

    # 执行查询
    models_result = await db.execute(query)
    models = models_result.scalars().all()

    # 构建响应，添加vendor_name
    model_responses = []
    for model in models:
        model_dict = {
            "id": model.id,
            "name": model.name,
            "model": model.model,
            "type": model.type,
            "vendorId": model.vendor_id,
            "vendorName": model.vendor_obj.name if model.vendor_obj else None,
            "apiKey": model.api_key,
            "baseUrl": model.base_url,
            "description": model.description,
            "isActive": model.is_active,
            "isDefault": model.is_default,
            "createdAt": model.created_at,
            "updatedAt": model.updated_at
        }
        model_responses.append(ModelResponse(**model_dict))

    return ModelListResponse(
        total=total,
        items=model_responses
    )


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型详情"""
    from sqlalchemy.orm import joinedload
    model = await db.execute(
        select(Model).options(joinedload(Model.vendor_obj)).where(Model.id == model_id)
    )
    model = model.scalar()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    
    # 构建响应，添加vendor_name
    model_dict = {
        "id": model.id,
        "name": model.name,
        "model": model.model,
        "type": model.type,
        "vendorId": model.vendor_id,
        "vendorName": model.vendor_obj.name if model.vendor_obj else None,
        "apiKey": model.api_key,
        "baseUrl": model.base_url,
        "description": model.description,
        "isActive": model.is_active,
        "isDefault": model.is_default,
        "createdAt": model.created_at,
        "updatedAt": model.updated_at
    }
    return ModelResponse(**model_dict)


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    model_in: ModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型"""
    from sqlalchemy.orm import joinedload
    model = await db.execute(
        select(Model).options(joinedload(Model.vendor_obj)).where(Model.id == model_id)
    )
    model = model.scalar()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    # 获取当前模型数据
    current_data = {
        'id': model.id,
        'name': model.name,
        'model': model.model,
        'type': model.type,
        'vendor_id': model.vendor_id,
        'api_key': model.api_key,
        'base_url': model.base_url,
        'description': model.description
    }

    # 更新模型字段
    update_data = model_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        current_data[field] = value

    # 验证更新后的模型配置
    await validate_model(current_data)

    # 应用更新
    for field, value in update_data.items():
        setattr(model, field, value)

    await db.commit()
    await db.refresh(model)
    
    # 重新加载vendor关联
    if model.vendor_id:
        vendor = await db.execute(select(ModelVendor).where(ModelVendor.id == model.vendor_id))
        model.vendor_obj = vendor.scalar()
    
    # 构建响应，添加vendor_name
    model_dict = {
        "id": model.id,
        "name": model.name,
        "model": model.model,
        "type": model.type,
        "vendorId": model.vendor_id,
        "vendorName": model.vendor_obj.name if model.vendor_obj else None,
        "apiKey": model.api_key,
        "baseUrl": model.base_url,
        "description": model.description,
        "isActive": model.is_active,
        "isDefault": model.is_default,
        "createdAt": model.created_at,
        "updatedAt": model.updated_at
    }
    return ModelResponse(**model_dict)


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型"""
    model = await db.execute(select(Model).where(Model.id == model_id))
    model = model.scalar()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    await db.delete(model)
    await db.commit()
    return {"message": "模型删除成功"}


@router.put("/{model_id}/set-default", response_model=ModelResponse)
async def set_default_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """设置模型为默认模型"""
    # 获取要设置为默认的模型
    model = await db.execute(select(Model).where(Model.id == model_id))
    model = model.scalar()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    # 取消同类型其他模型的默认状态
    await db.execute(
        Model.__table__.update()
        .where(Model.type == model.type, Model.id != model_id)
        .values(is_default=False)
    )

    # 设置当前模型为默认
    model.is_default = True
    await db.commit()
    await db.refresh(model)

    # 重新加载vendor关联
    if model.vendor_id:
        from sqlalchemy.orm import joinedload
        model_with_vendor = await db.execute(
            select(Model).options(joinedload(Model.vendor_obj)).where(Model.id == model_id)
        )
        model = model_with_vendor.scalar()

    # 构建响应
    model_dict = {
        "id": model.id,
        "name": model.name,
        "model": model.model,
        "type": model.type,
        "vendorId": model.vendor_id,
        "vendorName": model.vendor_obj.name if model.vendor_obj else None,
        "apiKey": model.api_key,
        "baseUrl": model.base_url,
        "description": model.description,
        "isActive": model.is_active,
        "isDefault": model.is_default,
        "createdAt": model.created_at,
        "updatedAt": model.updated_at
    }
    return ModelResponse(**model_dict)


# 模型厂商相关端点
@router.get("/vendor/list", response_model=ModelVendorListResponse)
async def list_model_vendors(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型厂商列表"""
    # 计算总数
    count_query = select(func.count(ModelVendor.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    offset = (page - 1) * page_size
    query = select(ModelVendor).offset(offset).limit(page_size)

    # 执行查询
    vendors_result = await db.execute(query)
    vendors = vendors_result.scalars().all()

    return ModelVendorListResponse(
        total=total,
        items=vendors
    )


@router.get("/vendor/{vendor_id}", response_model=ModelVendorResponse)
async def get_model_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型厂商详情"""
    vendor = await db.execute(select(ModelVendor).where(ModelVendor.id == vendor_id))
    vendor = vendor.scalar()
    if not vendor:
        raise HTTPException(status_code=404, detail="模型厂商不存在")
    return vendor


@router.post("/vendor", response_model=ModelVendorResponse)
async def create_model_vendor(
    vendor_in: ModelVendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新模型厂商"""
    # 检查是否已存在同名厂商
    existing_vendor = await db.execute(
        select(ModelVendor).where(ModelVendor.name == vendor_in.name)
    )
    if existing_vendor.scalar():
        raise HTTPException(status_code=400, detail="已存在同名模型厂商")

    # 创建新厂商
    vendor = ModelVendor(
        id=vendor_in.id,
        name=vendor_in.name,
        description=vendor_in.description or ""
    )
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


@router.put("/vendor/{vendor_id}", response_model=ModelVendorResponse)
async def update_model_vendor(
    vendor_id: str,
    vendor_in: ModelVendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型厂商"""
    vendor = await db.execute(select(ModelVendor).where(ModelVendor.id == vendor_id))
    vendor = vendor.scalar()
    if not vendor:
        raise HTTPException(status_code=404, detail="模型厂商不存在")

    # 检查是否与其他厂商重名
    if vendor_in.name and vendor_in.name != vendor.name:
        existing_vendor = await db.execute(
            select(ModelVendor).where(ModelVendor.name == vendor_in.name)
        )
        if existing_vendor.scalar():
            raise HTTPException(status_code=400, detail="已存在同名模型厂商")

    # 更新厂商字段
    update_data = vendor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    await db.commit()
    await db.refresh(vendor)
    return vendor


@router.delete("/vendor/{vendor_id}")
async def delete_model_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型厂商"""
    # 检查是否有关联的模型
    associated_models = await db.execute(
        select(Model).where(Model.vendor_id == vendor_id)
    )
    if associated_models.scalar():
        raise HTTPException(status_code=400, detail="该厂商下还有关联的模型，无法删除")

    vendor = await db.execute(select(ModelVendor).where(ModelVendor.id == vendor_id))
    vendor = vendor.scalar()
    if not vendor:
        raise HTTPException(status_code=404, detail="模型厂商不存在")

    await db.delete(vendor)
    await db.commit()
    return {"message": "模型厂商删除成功"}
