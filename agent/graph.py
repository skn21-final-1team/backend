from langgraph.graph import END, START, StateGraph

from agent.edges.route_by_intent import route_by_intent
from agent.nodes.classify_intent import classify_intent
from agent.nodes.generate_answer import generate_answer, generate_casual_answer
from agent.nodes.retrieve_sources import retrieve_sources
from agent.nodes.save_chat import save_chat
from agent.state import QAState

workflow = StateGraph(QAState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_sources", retrieve_sources)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("casual_answer", generate_casual_answer)
workflow.add_node("save_chat", save_chat)

workflow.add_edge(START, "classify_intent")
workflow.add_conditional_edges("classify_intent", route_by_intent)
workflow.add_edge("retrieve_sources", "generate_answer")
workflow.add_edge("generate_answer", "save_chat")
workflow.add_edge("casual_answer", "save_chat")
workflow.add_edge("save_chat", END)

graph = workflow.compile()
