from langgraph.graph import END, START, StateGraph

from agent.nodes.final import finalize_report
from agent.nodes.prepared import prepare_draft
from agent.nodes.requirement import analyze_requirement
from agent.nodes.skeleton import build_skeleton
from agent.workflow_state import WorkflowState

workflow = StateGraph(WorkflowState)

workflow.add_node("requirement", analyze_requirement)
workflow.add_node("skeleton", build_skeleton)
workflow.add_node("prepared", prepare_draft)
workflow.add_node("final", finalize_report)

workflow.add_edge(START, "requirement")
workflow.add_edge("requirement", "skeleton")
workflow.add_edge("skeleton", "prepared")
workflow.add_edge("prepared", "final")
workflow.add_edge("final", END)

report_graph = workflow.compile()
