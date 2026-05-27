from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from worker.grading.nodes import (
    parse_rubric,
    evaluate_partial_credit,
    check_plagiarism_node,
    write_result
)


class GradeState(TypedDict):
    grade_id: str
    question_id: str
    transcription: str
    question_rubric: dict
    max_marks: int
    ai_score: int
    breakdown: list
    justification: str
    plagiarism_flag: bool


def run_grading_graph(grade_id: str):
    graph = StateGraph(GradeState)

    graph.add_node("parse_rubric",   parse_rubric)
    graph.add_node("evaluate",       evaluate_partial_credit)
    graph.add_node("plagiarism",     check_plagiarism_node)
    graph.add_node("write",          write_result)

    graph.set_entry_point("parse_rubric")
    graph.add_edge("parse_rubric",  "evaluate")
    graph.add_edge("evaluate",      "plagiarism")
    graph.add_edge("plagiarism",    "write")
    graph.add_edge("write",         END)

    app = graph.compile()
    app.invoke({
        "grade_id": grade_id,
        "question_id": "",
        "transcription": "",
        "question_rubric": {},
        "max_marks": 10,
        "ai_score": 0,
        "breakdown": [],
        "justification": "",
        "plagiarism_flag": False
    })