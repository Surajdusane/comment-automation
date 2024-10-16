from client.client import supabase
from datetime import date
from modules.link_to_id import url_to_mediaid
from modules.comment import comment_on_post
import json

today = date.today().isoformat()

#Geting session id from db
sessionid_list = []
try:
    sessionidfromdb = supabase.table("session_id").select("*").execute()

    if sessionidfromdb.data:
        for sessionid in sessionidfromdb.data:
            session_id = {"sessionid":sessionid.get("session_id"), "id":sessionid.get("id"), "total_use": (sessionid.get("total_use"))}
            if session_id:
                sessionid_list.append(session_id)
except Exception as e:
    print(f"An error occurred: {e}")

numberofaccounts = len(sessionid_list)

#Geting post id and comment text from db
task_list = supabase.table('tasks').select('*').eq('is_executed', False).limit(numberofaccounts).execute().data
task_list = list(task_list)
print(task_list)
#Set api parameters
api_parameters = []

for i in range(len(task_list)):
    data_id = sessionid_list[i]["id"]
    link = task_list[i]["link"]
    post_id = url_to_mediaid(link)
    caomment = task_list[i]["comment_text"]
    acsessionid = sessionid_list[i]["sessionid"]
    acdbid = task_list[i]["id"] 
    total_use = int(list(sessionid_list[i]["total_use"].values())[0])
    taskdata = {
        "session_id_db_id": data_id,
        "post_id": post_id,
        "comment_text": caomment,
        "session_id": acsessionid,
        "tasks_db_id": acdbid,
        "total_use": total_use
    }
    api_parameters.append(taskdata)


# Posting comment to instagram
for i in range(len(api_parameters)):
    print(api_parameters[i])
    comment_results = comment_on_post(api_parameters[i]["session_id"], api_parameters[i]["post_id"], api_parameters[i]["comment_text"])
    if comment_results:
        supabase.table("tasks").update({"is_executed": True}).eq("id", api_parameters[i]["tasks_db_id"]).execute()
        supabase.table("session_id").update({"total_use": {today: int(total_use) + 1}}).eq("id", api_parameters[i]["tasks_db_id"]).execute()
        print(f"Comment posted successfully for task {api_parameters[i]['tasks_db_id']}")
    else:
        supabase.table("tasks").update({"is_executed": False}).eq("id", api_parameters[i]["tasks_db_id"]).execute()
        print(f"Failed to post comment for task {api_parameters[i]['tasks_db_id']}")