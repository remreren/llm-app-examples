from langchain_community.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type, Tuple, Optional

class CreateTaskModel(BaseModel):
    """Input for the Create Task tool."""

    task_list_id: str = Field(description="Task list ID to create the task in")
    task_title: str = Field(description="Title of the task to create")
    task_notes: str = Field(description="Notes for the task to create", default=None)

class CreateTask(BaseTool):
    """Tool that interacts with Google Tasks API to manage tasks.

    Setup:
      Install ``google-api-python-client`` and set up OAuth 2.0 credentials.

      .. code-block:: bash

        pip install google-api-python-client
        # Follow the instructions to set up OAuth 2.0 credentials and save the client_secret.json file

    Instantiate:

      .. code-block:: python
      
        from task_manager.gtasks_tool import GtasksTool
        
        tool = GtasksTool()

    Invoke directly with args:

      .. code-block:: python

        tool.create_task(task_list_id, task_title, task_notes)
    
    Invoke with tool call:

      .. code-block:: python

        tool.create_task.run(task_list_id, task_title, task_notes)

    """  # noqa: E501

    name: str = "create_task"
    args_schema: Type[BaseModel] = CreateTaskModel
    description = "Create a new task in a specified task list."
    return_direct: bool = True

    def _run(
        self,
        task_list_id: str,
        task_title: str,
        task_notes: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[dict, dict]:
        """Create a new task in a specified task list."""
        raw_results = create_task(task_list_id, task_title, task_notes)
        return raw_results

    async def _arun(
        self,
        task_list_id: str,
        task_title: str,
        task_notes: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return self._run(task_list_id=task_list_id, task_title=task_title, task_notes=task_notes, run_manager=run_manager.get_sync())
