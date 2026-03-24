"""
LangGraph 简单案例HelloWorld：
构建一个最小的有向图，流程是：START → 模型节点 → END

LangGraph的灵魂：State(状态) + Nodes(节点) + Edges(边) + Graph(图)
"""

import uuid
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

# ========== 1. 定义状态（State） ==========
# 存储对话消息
class AtguiguState(TypedDict):
    # messages 是一个消息列表，Annotated + add_messages 表示支持自动追加消息
    messages: Annotated[List, add_messages]

# ========== 2. 定义大模型 ==========
llm = init_chat_model(
    model="qwen-max",
    model_provider="openai",
    api_key="sk-b54299feefc6431f95014b4e3eb86bef",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# ========== 3. 定义节点函数 ==========
# 节点：调用大模型，并把回复加入到 state["messages"] 里
def model_node(state: AtguiguState):
    reply = llm.invoke(state["messages"])   # 输入历史消息，调用模型
    return {"messages": [reply]}            # 返回新消息，自动加到 state

graph = StateGraph(AtguiguState)
graph.add_node("model",model_node)

graph.add_edge(START, "model")
graph.add_edge("model", END)

app = graph.compile()
result = app.invoke({"messages": "请用一句话解释什么是 LangGraph。"})

# 打印模型的最后一条回复
print("模型回答：", result["messages"][-1].content)

