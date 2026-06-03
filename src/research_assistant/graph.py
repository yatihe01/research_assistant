from langgraph.graph import END, START, StateGraph

from research_assistant.base_rag import retrieve_base_context
from research_assistant.critic import critique_new_idea
from research_assistant.literature import search_literature
from research_assistant.state import GraphState
from research_assistant.storage import append_idea
from research_assistant.summarizer import summarize_idea


def router(state: GraphState) -> GraphState:
    return {"input_type": state.get("input_type", "new_idea")}


def summarize(state: GraphState) -> GraphState:
    return {"summary": summarize_idea(state["input_text"])}


def retrieve_base(state: GraphState) -> GraphState:
    query = state.get("summary", {}).get("statement") or state["input_text"]
    return {"base_context": retrieve_base_context(query)}


def search_lit(state: GraphState) -> GraphState:
    return {"literature": search_literature(state.get("summary", {}))}


def interpret_result(state: GraphState) -> GraphState:
    return {
        "result_analysis": {
            "vs_hypothesis": "Result interpretation is not implemented in Phase 1.",
            "vs_baseline": "Result interpretation is not implemented in Phase 1.",
            "metrics": {},
            "surprises": [],
        }
    }


def critic(state: GraphState) -> GraphState:
    return {
        "critique": critique_new_idea(
            summary=state.get("summary", {}),
            base_context=state.get("base_context", []),
            literature=state.get("literature", []),
        ),
        "new_status": "proposed",
    }


def human_checkpoint(state: GraphState) -> GraphState:
    return {"approved": True, "user_edits": None}


def persist(state: GraphState) -> GraphState:
    idea_id = append_idea(
        summary=state["summary"],
        critique=state.get("critique", "Critic not implemented in Phase 1."),
        status=state.get("new_status", "proposed"),
    )
    return {"persisted_idea_id": idea_id}


def update_idea(state: GraphState) -> GraphState:
    return state


def build_phase2_graph():
    graph = StateGraph(GraphState)
    graph.add_node("router", router)
    graph.add_node("summarize", summarize)
    graph.add_node("retrieve_base", retrieve_base)
    graph.add_node("search_lit", search_lit)
    graph.add_node("interpret_result", interpret_result)
    graph.add_node("critic", critic)
    graph.add_node("human_checkpoint", human_checkpoint)
    graph.add_node("persist", persist)
    graph.add_node("update_idea", update_idea)

    graph.add_edge(START, "router")
    graph.add_edge("router", "summarize")
    graph.add_edge("summarize", "retrieve_base")
    graph.add_edge("retrieve_base", "search_lit")
    graph.add_edge("search_lit", "critic")
    graph.add_edge("critic", "human_checkpoint")
    graph.add_edge("human_checkpoint", "persist")
    graph.add_edge("persist", END)
    return graph.compile()


def process_new_idea(input_text: str) -> GraphState:
    graph = build_phase2_graph()
    return graph.invoke({"input_text": input_text, "input_type": "new_idea"})


build_phase1_graph = build_phase2_graph
