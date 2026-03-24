'''
我们先在不接入大模型的情况下构建一个加减法图工作流，
我们这里自定义两个简单函数：一个是加法函数接收当前State并将其中的x值加1，
另一个是减法函数接收当前State并将其中的x值减2，
然后添加名为addition和subtraction的节点，并关联到两个函数上，最后构建出节点之间的边。
'''


from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END
import uuid

def addition(state):
    print(f"加法节点开始执行，输入参数为：{state}·")
    return {"x": state["x"] + 1}

def subtraction(state):
    print(f"减法节点开始执行，输入参数为：{state}·")
    return {"x": state["x"] - 2}

graph = StateGraph(dict)
graph.add_node("addition",addition)
graph.add_node("subtraction",subtraction)

graph.add_edge(START, "addition")
graph.add_edge("addition","subtraction")
graph.add_edge("subtraction", END)

app = graph.compile()
result = app.invoke({"x": 1})
print(result)
print(result["x"])
