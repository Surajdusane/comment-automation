import logging
from datetime import datetime, timedelta
from client.client import supabase
from fastapi import FastAPI, HTTPException, BackgroundTasks
from modules.link_to_id import url_to_mediaid
from modules.comment import comment_on_post

# Client setup
from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_valid_session_ids():
    try:
        now = datetime.now()
        ten_minutes_ago = now - timedelta(minutes=10)
        
        sessionidfromdb = supabase.table("session_id").select("*").execute()
        
        valid_sessions = []
        for session in sessionidfromdb.data:
            if session.get("session_id") and session.get("id"):
                total_use = sum(session.get("total_use", {}).values())
                last_used = session.get("last_used")
                
                if total_use >= 40:
                    continue
                
                if last_used:
                    last_used_time = datetime.fromisoformat(last_used)
                    if last_used_time > ten_minutes_ago:
                        continue
                
                valid_sessions.append({
                    "sessionid": session["session_id"],
                    "id": session["id"],
                    "total_use": session.get("total_use", {}),
                    "last_used": last_used
                })
        
        return valid_sessions
    except Exception as e:
        logger.error(f"Failed to fetch valid session IDs: {e}")
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

def update_task_status(task_id, is_executed, execution_time=None):
    try:
        update_data = {"is_executed": is_executed}
        if execution_time:
            update_data["execution_time"] = execution_time
        supabase.table("tasks").update(update_data).eq("id", task_id).execute()
    except Exception as e:
        logger.error(f"Failed to update task status for task {task_id}: {e}")

def update_session_usage(session_id, total_use):
    today = datetime.now().date().isoformat()
    now = datetime.now().isoformat()
    try:
        new_total_use = total_use.copy()
        new_total_use[today] = new_total_use.get(today, 0) + 1
        supabase.table("session_id").update({
            "total_use": new_total_use,
            "last_used": now
        }).eq("id", session_id).execute()
    except Exception as e:
        logger.error(f"Failed to update usage for session {session_id}: {e}")

def process_comment_task(api_parameters):
    comments_posted = 0
    for params in api_parameters:
        try:
            comment_results = comment_on_post(params["session_id"], params["post_id"], params["comment_text"])
            if comment_results:
                execution_time = datetime.now().isoformat()
                update_task_status(params["tasks_db_id"], True, execution_time)
                update_session_usage(params["session_id_db_id"], params["total_use"])
                comments_posted += 1
                logger.info(f"Comment posted successfully for task {params['tasks_db_id']}")
            else:
                update_task_status(params["tasks_db_id"], False)
                logger.warning(f"Failed to post comment for task {params['tasks_db_id']}")
        except Exception as e:
            logger.error(f"Error processing task {params['tasks_db_id']}: {e}")

@app.get("/")
async def root():
    return {"ok"}

@app.get("/execute-comment-bot")
async def execute_comment_bot(background_tasks: BackgroundTasks):
    try:
        session_ids = get_valid_session_ids()
        if not session_ids:
            logger.warning("No valid session IDs found. Exiting.")
            return {"message": "No valid session IDs found", "comments_posted": 0}

        tasks = get_tasks(len(session_ids))
        if not tasks:
            logger.info("No tasks found. Exiting.")
            return {"message": "No tasks found", "comments_posted": 0}

        api_parameters = prepare_api_parameters(session_ids, tasks)
        
        # Run the task processing in the background
        background_tasks.add_task(process_comment_task, api_parameters)

        # Return a quick response to avoid long execution time
        return {"message": "OK"}

    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, port=8000)
