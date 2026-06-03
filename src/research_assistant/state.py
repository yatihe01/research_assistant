from typing import Literal, Optional, TypedDict


Status = Literal["proposed", "testing", "supported", "refuted", "inconclusive"]
InputType = Literal["new_idea", "result"]


class GraphState(TypedDict, total=False):
    input_text: str
    input_type: InputType
    target_idea_id: Optional[str]

    summary: dict

    base_context: list[str]
    literature: list[dict]

    result_analysis: dict

    critique: str
    new_status: Status
    approved: bool
    user_edits: Optional[str]

    persisted_idea_id: str
