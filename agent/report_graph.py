from langgraph.graph import START, StateGraph

from agent.edges.route_report_workflow import route_report_workflow
from agent.nodes.await_user_review import await_user_review
from agent.nodes.filter_source import filter_source
from agent.nodes.final import finalize_report
from agent.nodes.prepared import prepare_draft
from agent.nodes.requirement import analyze_requirement
from agent.nodes.review_decision import review_decision
from agent.nodes.skeleton import build_skeleton
from agent.workflow_state import WorkflowState
from db.report_workflow_checkpoint_saver import report_workflow_checkpoint_saver

workflow = StateGraph(WorkflowState)

workflow.add_node("filter_source", filter_source)
workflow.add_node("requirement", analyze_requirement)
workflow.add_node("skeleton", build_skeleton)
workflow.add_node("prepared", prepare_draft)
workflow.add_node("final", finalize_report)
workflow.add_node("await_user_review", await_user_review)
workflow.add_node("review_decision", review_decision)

workflow.add_edge(START, "filter_source")
workflow.add_edge("filter_source", "requirement")
workflow.add_edge("requirement", "await_user_review")
workflow.add_edge("skeleton", "await_user_review")
workflow.add_edge("prepared", "await_user_review")
workflow.add_edge("final", "await_user_review")
workflow.add_edge("await_user_review", "review_decision")
workflow.add_conditional_edges("review_decision", route_report_workflow)

report_graph = workflow.compile(checkpointer=report_workflow_checkpoint_saver)
