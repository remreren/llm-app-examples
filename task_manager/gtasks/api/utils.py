from typing import List

from .typing import TasksResponse

def build_task_hierarchy(task_list: TasksResponse) -> List[dict]:
    task_dict = {tsk.id: tsk.model_dump() for tsk in task_list.items}

    # Prepare a dictionary to hold parent-child relationships
    task_hierarchy = {}

    # First, populate the top-level tasks (without a parent)
    for task_id, task in task_dict.items():
        parent_id = task.get('parent')
        if not parent_id:
            # If no parent, it's a top-level task
            task_hierarchy[task_id] = task
            task_hierarchy[task_id]['children'] = []

    # Now, assign children to their respective parents
    for task_id, task in task_dict.items():
        parent_id = task.get('parent')
        if parent_id:
            if parent_id in task_hierarchy:
                task_hierarchy[parent_id]['children'].append(task)
            else:
                # Parent not found at top level, nest it as a child of its parent
                # task_hierarchy[parent_id] = {'children': [task], **task_dict.get(parent_id, {})}
                pass

    # Return only the top-level tasks (parents) with their nested children
    return [task for task in task_hierarchy.values() if not task.get('parent')]


def build_yaml_task_hierarchy(tasks: List[dict]) -> List[dict]:
    result = []
    
    for task in tasks:
        try:
            task_entry = {
                'id': task['id'],
                'title': task['title'],
                'notes': task.get('notes', ''),
                'status': repr(task.get('status', 'unknown')),
            }
            if 'children' in task and task['children']:
                task_entry['children'] = build_yaml_task_hierarchy(task['children'])  # Recursive for children
            result.append(task_entry)
        except Exception as e:
            print(f"Error processing task: {task}")
            raise e
    return result
