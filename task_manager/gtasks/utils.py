from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

def _print_event(event: dict, _printed: set, max_length=2000):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

# create an agent system to run an llm and search for information on tavily via function call
def handle_tool_error(state) -> dict:
    """
    Function to handle errors that occur during tool execution.

    Args:
        state (dict): The current state of the AI agent, which includes messages and tool call details.

    Returns:
        dict: A dictionary containing error messages for each tool that encountered an issue.
    """
    # Retrieve the error from the current state
    error = state.get("error")

    # Access the tool calls from the last message in the state's message history
    tool_calls = state["messages"][-1].tool_calls

    # Return a list of ToolMessages with error details, linked to each tool call ID
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",  # Format the error message for the user
                tool_call_id=tc[
                    "id"
                ],  # Associate the error message with the corresponding tool call ID
            )
            for tc in tool_calls  # Iterate over each tool call to produce individual error messages
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    """
    Function to create a tool node with fallback error handling.

    Args:
        tools (list): A list of tools to be included in the node.

    Returns:
        dict: A tool node that uses fallback behavior in case of errors.
    """
    # Create a ToolNode with the provided tools and attach a fallback mechanism
    # If an error occurs, it will invoke the handle_tool_error function to manage the error
    return ToolNode(tools).with_fallbacks(
        [
            RunnableLambda(handle_tool_error)
        ],  # Use a lambda function to wrap the error handler
        exception_key="error",  # Specify that this fallback is for handling errors
    )