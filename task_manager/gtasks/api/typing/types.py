from typing import Optional, List

from enum import Enum
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    needsAction = 'needsAction'
    completed = 'completed'

    def __repr__(self):
        return self.value

class TaskLink(BaseModel):
    type: str = Field(..., description="Type of the link.")
    description: str = Field(..., description="Description of the link.")
    link: str = Field(..., description="URL.")

class Task(BaseModel):
    kind: str = Field(..., description="Type of the resource. This is always 'tasks#task'.")
    id: str = Field(..., description="Task identifier.")
    etag: str = Field(..., description="ETag of the resource.")
    title: Optional[str] = Field(None, description="Title of the task.")
    updated: str = Field(..., description="Last modification time of the task (as a RFC 3339 timestamp).")
    selfLink: str = Field(..., description="URL pointing to this task.")
    parent: Optional[str] = Field(None, description="Parent task identifier. This field is omitted if it is a top-level task.")
    position: str = Field(..., description="String indicating the position of the task among its sibling tasks.")
    notes: Optional[str] = Field(None, description="Notes describing the task.")
    status: Optional[TaskStatus] = Field(None, description="Status of the task. This is either 'needsAction' or 'completed'.")
    due: Optional[str] = Field(None, description="Due date of the task (as a RFC 3339 timestamp).")
    completed: Optional[str] = Field(None, description="Completion date of the task (as a RFC 3339 timestamp).")
    deleted: Optional[bool] = Field(None, description="Flag indicating whether the task has been deleted. The default is False.")
    hidden: Optional[bool] = Field(None, description="Flag indicating whether the task is hidden. The default is False.")
    links: Optional[List[TaskLink]] = Field(None, description="Collection of links associated with this task.")


class TasksResponse(BaseModel):
    kind: str = Field(..., description="Type of the resource. This is always 'tasks#tasks'.")
    etag: str = Field(..., description="ETag of the resource.")
    items: Optional[List[Task]] = Field(None, description="Collection of items.")

class TaskList(BaseModel):
    kind: str = Field(..., description="Type of the resource. This is always 'tasks#taskList'.")
    id: str = Field(..., description="Task list identifier.")
    etag: str = Field(..., description="ETag of the resource.")
    title: str = Field(..., description="Title of the task list.")
    updated: str = Field(..., description="Last modification time of the task list (as a RFC 3339 timestamp).")
    selfLink: str = Field(..., description="URL pointing to this task list.")

class TaskListsReponse(BaseModel):
    kind: str = Field(..., description="Type of the resource. This is always 'tasks#taskLists'.")
    etag: str = Field(..., description="ETag of the resource.")
    items: Optional[List[TaskList]] = Field(None, description="Collection of items.")
