from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, START, END
import uuid

class HelloState(TypedDict):
    name: str
    greeting: str

def greet(helloState: HelloState) -> dict:
    name = helloState["name"]
    return {"greeting": f"你好,{name}"}

def add_emoji(hellState: HelloState) -> dict:
    greeting = hellState["greeting"]
    return {"greeting": greeting + "。。。"}

graph = StateGraph(HelloState)
graph.add_node("greeting", greet)
graph.add_node("add_emoji", add_emoji)

graph.add_edge(START, "greeting")
graph.add_edge("greeting", "add_emoji")
graph.add_edge("add_emoji", END)

app = graph.compile()

result = app.invoke({"name": "张三"})
print(result)
print(result["greeting"])

#
# #6 打印图的边和节点信息
#6.1 打印图的ascii可视化结构
print(app.get_graph().print_ascii())
print("="*50)
#
# #6.2 打印图的Mermaid代码可视化结构并通过https://www.processon.com/mermaid编辑器查看
print(app.get_graph().draw_mermaid())
print("="*50)