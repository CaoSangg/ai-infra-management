# layer2_ai_agent/graph.py

from langgraph.graph import StateGraph, START, END
from ai_agent.nodes.node1_intent import analyze_intent, AgentState
from ai_agent.nodes.node2_planner import generate_plan

# 1. Khởi tạo đồ thị với State đã định nghĩa
workflow = StateGraph(AgentState)

# 2. Thêm các Node vào đồ thị
workflow.add_node("node1_intent", analyze_intent)
workflow.add_node("node2_planner", generate_plan)

# 3. Nối luồng (Edges) định tuyến luồng dữ liệu
workflow.add_edge(START, "node1_intent")
workflow.add_edge("node1_intent", "node2_planner")
workflow.add_edge("node2_planner", END)

# 4. Biên dịch đồ thị thành một ứng dụng có thể chạy được
app_graph = workflow.compile()
