import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from typing import Optional
from gtasks.api.typing import TasksResponse, TaskListsResponse, Task, TaskList

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/tasks.readonly",
]

creds = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=12345)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("tasks", "v1", credentials=creds)


def get_task_list(task_list_id: str) -> TaskList:
    return TaskList(**(service.tasklists().get(tasklist=task_list_id).execute()))


def get_task_lists(max_results=5) -> TaskListsResponse:
    return TaskListsResponse(
        **(
            service.tasklists()
            .list(
                maxResults=max_results,
            )
            .execute()
        )
    )


def get_tasks(task_list_id, showCompleted=False, showDeleted=False) -> TasksResponse:
    return TasksResponse(
        **(
            service.tasks()
            .list(
                tasklist=task_list_id,
                showCompleted=showCompleted,
                showDeleted=showDeleted,
            )
            .execute()
        )
    )


def upsert_task(task_list_id: Optional[str], task: Task) -> Task:
    """
    Insert or update a task in the task list.

    If the task ID is provided, the task will be updated.
    Otherwise, a new task will be created.

    :param task_list_id: Task list ID.
    :param task: Task object.
    :return: Task object.
    """

    if task.id:
        return Task(
            **(
                service.tasks()
                .patch(tasklist=task_list_id, task=task.id, body=task.model_dump(exclude_none=True))
                .execute()
            )
        )
    else:
        return Task(
            **(
                service.tasks()
                .insert(tasklist=task_list_id, body=task.model_dump(exclude_none=True))
                .execute()
            )
        )
