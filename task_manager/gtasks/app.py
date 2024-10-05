import uuid

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.prebuilt import tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

from .utils import _print_event, create_tool_node_with_fallback
from .tools import GetTaskLists, UpsertTask, GetTasks


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        # Initialize with the runnable that defines the process for interacting with the tools
        self.runnable = runnable

    def __call__(self, state: State):
        while True:
            # Invoke the runnable with the current state (messages and context)
            result = self.runnable.invoke(state)

            # If the tool fails to return valid output, re-prompt the user to clarify or retry
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                # Add a message to request a valid response
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                # Break the loop when valid output is obtained
                break

        # Return the final state after processing the runnable
        return {"messages": result}

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

assistant_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant.
            You should follow the instructions given by the user using the tools available.
            The order is important. Use these steps for using tools:
            1. If any extra information is needed, ask the user.
            2. If every detail is clear, proceed with the commands.
            3. If there is an error, prompt the user to fix it.

            Using search:
            1. If the user asks for information, first create a plan to search for it.
            2. After planning, execute the search using the tools available.
            
            Using task management tools:
            1. If the user asks to perform a command, use the tools to complete it.
            2. If user asks for a task to be added or edited, check first if it exists.
            2.1. First destination is to search for the task without asking for task list ID.
            2.2. If the task is not found, add task to an appropriate list.
            2.3. If there is no appropriate list, ask the user to provide the list name.

            If you are not able to discern any info, ask them to clarify! Do not attempt to wildly guess.
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)

tools = [
    GetTaskLists(),
    GetTasks(),
    UpsertTask(),
]

assistant = assistant_template | llm.bind_tools(tools)

builder = StateGraph(State)
builder.add_node("assistant", Assistant(assistant))
builder.add_node("tools", create_tool_node_with_fallback(tools))

builder.add_edge(START, "assistant")  # Start with the assistant
builder.add_conditional_edges("assistant", tools_condition)  # Move to tools after input
builder.add_edge("tools", "assistant")  # Return to assistant after tool execution

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        "thread_id": thread_id,
    },
    # "callbacks": [langfuse_handler],
}

# ----


def run_commands(commands):
    _printed = set()
    for command in commands:
        events = graph.stream(
            {"messages": ("user", command)}, config=config, stream_mode="values"
        )
        for event in events:
            _print_event(event, _printed, max_length=2000)
