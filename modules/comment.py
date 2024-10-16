import requests
import json

def comment_on_post(session_id, post_id, comment_text):
    # Instagram API endpoint for commenting
    url = f"https://www.instagram.com/api/v1/web/comments/{post_id}/add/"

    # Headers required for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "X-CSRFToken": session_id,  # Using session_id as CSRF token
        "Cookie": f"sessionid={session_id};",
    }

    # Data to be sent in the request
    data = {
        "comment_text": comment_text,
        "replied_to_comment_id": "",
    }

    # Send POST request to comment on the post
    response = requests.post(url, headers=headers, data=data)

    # if response.status_code == 200:
    #     print("Comment posted successfully!")
    #     return json.loads(response.text)
    # else:
    #     print(f"Failed to post comment. Status code: {response.status_code}")
    #     print(f"Response: {response.text}")
    #     return None
    if response.status_code == 200:
        print("Comment posted successfully!")
        return True
    else:
        print(f"Failed to post comment. Status code: {response.status_code}")
        return None

# Example usage
# session_id = '69678068297%3AnoOwfc21AjeXVc%3A15%3AAYd4X--Fhv6kqP--3oiZtiJJ5wXM1LgouSQJp4Wevg'
# post_id = "3117726179745102077"
# comment_text = "Great post!"

# result = comment_on_post(session_id, post_id, comment_text)
# if result:
#     print(f"Comment ID: {result['id']}")
#     print(f"Comment text: {result['text']}")