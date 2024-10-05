from langchain_community.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from pydantic import BaseModel, Field
from typing import Type, Tuple, Optional

from gtasks.api import get_task_lists


class GetTaskListsModel(BaseModel):
    """Input for the Get Task Lists tool."""

    pass


class GetTaskLists(BaseTool):
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

        tool.get_task_lists()

    Invoke with tool call:

      .. code-block:: python

        tool.get_task_lists.run

    """  # noqa: E501

    name: str = "get_task_lists"
    args_schema: Type[BaseModel] = GetTaskListsModel
    description = "Get all task lists."
    return_direct: bool = True

    def _run(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Tuple[dict, dict]:
        """Retrieve all task lists."""
        raw_results = get_task_lists()
        return raw_results

    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return self._run(run_manager=run_manager.get_sync())
