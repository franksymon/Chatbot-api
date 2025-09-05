from typing import TypedDict, List, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated

class ChatState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    provider: str
    session_id: str
    prompt_type: str
