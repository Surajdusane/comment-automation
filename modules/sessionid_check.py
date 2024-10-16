import requests

def check_instagram_session(session_id):
    url = "https://www.instagram.com/accounts/access_tool/login_activity/"

    # Set up headers including the session ID as a cookie
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    cookies = {
        "sessionid": session_id,
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            print("Session ID is alive.")
            return True
        else:
            print("Session ID is dead or invalid.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False

# if __name__ == "__main__":
#     session_id = "69678068297%3AnoOwfc21AjeXVc%3A15%3AAYd4X--Fhv6kqP--3oiZtiJJ5wXM1LgouSQJp4Wevg"
#     check_instagram_session(session_id)
