import logging
from datetime import date
from modules.link_to_id import url_to_mediaid
from modules.comment import comment_on_post
from client.client import supabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_session_ids():
    try:
        sessionidfromdb = supabase.table("session_id").select("*").execute()
        return [
            {
                "sessionid": session.get("session_id"),
                "id": session.get("id"),
                "total_use": session.get("total_use", {})
            }
            for session in sessionidfromdb.data if session.get("session_id") and session.get("id")
        ]
    except Exception as e:
        logger.error(f"Failed to fetch session IDs: {e}")
        return []

def get_tasks(limit):
    try:
        return supabase.table('tasks').select('*').eq('is_executed', False).limit(limit).execute().data
    except Exception as e:
        logger.error(f"Failed to fetch tasks: {e}")
        return []

def prepare_api_parameters(session_ids, tasks):
    api_parameters = []
    for i, task in enumerate(tasks):
        if i >= len(session_ids):
            break
        try:
            post_id = url_to_mediaid(task["link"])
            api_parameters.append({
                "session_id_db_id": session_ids[i]["id"],
                "post_id": post_id,
                "comment_text": task["comment_text"],
                "session_id": session_ids[i]["sessionid"],
                "tasks_db_id": task["id"],
                "total_use": session_ids[i]["total_use"]
            })
        except Exception as e:
            logger.error(f"Failed to prepare API parameters for task {task['id']}: {e}")
    return api_parameters

def update_task_status(task_id, is_executed):
    try:
        supabase.table("tasks").update({"is_executed": is_executed}).eq("id", task_id).execute()
    except Exception as e:
        logger.error(f"Failed to update task status for task {task_id}: {e}")

def update_total_use(session_id, total_use):
    today = date.today().isoformat()
    try:
        new_total_use = total_use.copy()
        new_total_use[today] = new_total_use.get(today, 0) + 1
        supabase.table("session_id").update({"total_use": new_total_use}).eq("id", session_id).execute()
    except Exception as e:
        logger.error(f"Failed to update total use for session {session_id}: {e}")

def main():
    session_ids = get_session_ids()
    if not session_ids:
        logger.error("No valid session IDs found. Exiting.")
        return

    tasks = get_tasks(len(session_ids))
    if not tasks:
        logger.info("No tasks found. Exiting.")
        return

    api_parameters = prepare_api_parameters(session_ids, tasks)

    for params in api_parameters:
        try:
            comment_results = comment_on_post(params["session_id"], params["post_id"], params["comment_text"])
            if comment_results:
                update_task_status(params["tasks_db_id"], True)
                update_total_use(params["session_id_db_id"], params["total_use"])
                logger.info(f"Comment posted successfully for task {params['tasks_db_id']}")
            else:
                update_task_status(params["tasks_db_id"], False)
                logger.warning(f"Failed to post comment for task {params['tasks_db_id']}")
        except Exception as e:
            logger.error(f"Error processing task {params['tasks_db_id']}: {e}")

if __name__ == "__main__":
    main()