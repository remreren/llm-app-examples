from langchain_community.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field
from typing import Type, Tuple, Optional

from gtasks.api import get_task_lists, get_task_list, get_tasks
from gtasks.api.typing import Task
from gtasks.api.utils import build_task_hierarchy, build_yaml_task_hierarchy

import yaml
import json

class GetTasksModel(BaseModel):
    """Input for the Get Task Lists tool."""

    # optional task list ids to retrieve
    task_list_ids: Optional[list[str]] = Field(
        None,
        description="Task list IDs to retrieve. This is optional. If not provided, first 5 task lists will be retrieved.",
    )

class TaskListResponse(BaseModel):
    """Response for the Get Task Lists tool."""

    id: str = Field(
        ...,
        description="Task list identifier.",
    )
    title: str = Field(
        ...,
        description="Title of the task list.",
    )
    items: list[Task] = Field(
        ...,
        description="Collection of items.",
    )


class GetTasks(BaseTool):
    """Tool that interacts with Google Tasks API to manage tasks.

    Setup:
      Install ``google-api-python-client`` and set up OAuth 2.0 credentials.

      .. code-block:: bash

        pip install google-api-python-client
        # Follow the instructions to set up OAuth 2.0 credentials and save the client_secret.json file

    Instantiate:

      .. code-block:: python

        from task_manager.gtasks import GetTasks

        tool = GetTasks()

    Invoke directly with args:

      .. code-block:: python

        tool.invoke({ "task_list_ids": ["task_list_id_1", "task_list_id_2"] })

    Invoke with tool call:

      .. code-block:: python

        tool.invoke({ "task_list_ids": ["task_list_id_1", "task_list_id_2"] })

    """  # noqa: E501

    name: str = "get_tasks"
    args_schema: Type[BaseModel] = GetTasksModel
    description = "Get tasks in a list or all tasks in lists with given ids."
    return_direct: bool = True

    def _run(
        self,
        task_list_ids: Optional[list[str]],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[dict, dict]:
        """Retrieve all task lists."""
        task_lists_ids: list[str] = task_list_ids or get_task_lists().items

        if not task_lists_ids:
            return "No task lists found.", {}
        
        if not isinstance(task_lists_ids, list):
            raise ValueError("Task lists must be a list.")

        task_lists: list[TaskListResponse] = []
        for task_list_id in task_lists_ids:
            task_list = get_task_list(task_list_id)
            tasks = get_tasks(task_list_id)

            hierarchical_tasks = build_task_hierarchy(tasks)
            yaml_tasks = build_yaml_task_hierarchy(hierarchical_tasks)

            task_lists.append(
                {
                    "id": task_list_id,
                    "title": task_list.title,
                    "items": yaml_tasks,
                }
            )

        return json.dumps(task_lists), task_lists

    async def _arun(
        self,
        task_list_ids: Optional[list[str]],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(task_list_ids=task_list_ids, run_manager=run_manager.get_sync())
