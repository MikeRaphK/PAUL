
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field
from typing import Annotated, Sequence, TypedDict


class PatchReport(BaseModel):
    """
    Structured response model for patch description and pull request creation.
    """
    commit_msg: str = Field(..., description="Concise git commit message describing the changes", examples=["Fix division by zero error in calculation module"])
    title: str = Field(..., description="Clear and descriptive patch title", examples=["Fix division by zero error in app calculation"])
    body: str = Field(..., description="Detailed patch description with context and changes", examples=["This patch fixes a critical bug that could cause a division by zero exception when processing empty input arrays. Added a conditional check to validate input before performing calculations, preventing runtime crashes and improving application stability."])


class PaulState(TypedDict):
    # Patcher
    patcher_llm: Runnable
    patcher_chat_history: Annotated[Sequence[BaseMessage], add_messages]
    write_tool_used: bool = False
    file_modified: str = None
    patcher_tokens: int = 0
    patcher_cost: float = 0.0

    # Verifier
    tests: list[str]
    tests_pass: bool = False
    venv: str = None
    failed_attempts: int = 0
    swe: bool = False
    quixbugs_verify_cmd: str = None

    # Reporter
    reporter_chain: Runnable
    reporter_chat_history: Annotated[Sequence[BaseMessage], add_messages]
    reporter_tokens: int = 0
    reporter_cost: float = 0.0
    report: PatchReport = None
