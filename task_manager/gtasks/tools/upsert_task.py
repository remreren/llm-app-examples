from langchain_community.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field

from typing import Type, Tuple, Optional
# from gtasks.api.typing import Task

from gtasks.api import upsert_task

from enum import Enum

class TaskStatus(str, Enum):
    needsAction = 'needsAction'
    completed = 'completed'

    def __repr__(self):
        return self.value

class Task(BaseModel):
    id: Optional[str] = Field(None, description="Task identifier.")
    title: str = Field(None, description="Title of the task.")
    parent: Optional[str] = Field(None, description="Parent task identifier. This field is omitted if it is a top-level task.")
    notes: Optional[str] = Field(None, description="Notes describing the task.")
    status: Optional[TaskStatus] = Field(TaskStatus.needsAction, description="Status of the task. This is either 'needsAction' or 'completed'.")
    due: Optional[str] = Field(None, description="Due date of the task (as a RFC 3339 timestamp).")
    completed: Optional[str] = Field(None, description="Completion date of the task (as a RFC 3339 timestamp).")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the task has been deleted. The default is False.")    

class UpsertTaskModel(BaseModel):
    """Input for the Create or Update Task tool."""

    task_list_id: Optional[str] = Field(description="Task list ID to create or update the task in")
    task: Task = Field(description="Task object to create or update")

class UpsertTask(BaseTool):
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

        tool.upsert_task(task_list_id, task)

    Invoke with tool call:

      .. code-block:: python

        tool.upsert_task.run(task_list_id, task)

    """  # noqa: E501

    name: str = "upsert_task"
    args_schema: Type[BaseModel] = UpsertTaskModel
    description = "Create or update a task in a specified task list."
    return_direct: bool = True

    def _run(
        self,
        task_list_id: Optional[str],
        task: Task,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[dict, dict]:
        """Create or update a task in a specified task list."""
        raw_results = upsert_task(task_list_id, task)
        return raw_results
    
    def _arun(
        self,
        task_list_id: Optional[str],
        task: Task,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""

        return self._run(task_list_id=task_list_id, task=task, run_manager=run_manager.get_sync())
