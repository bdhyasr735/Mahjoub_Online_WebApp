import requests

# التوكن الخاص بك
ACCESS_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
ENDPOINT = "https://mahjoub.online/admin/graphql"

def execute_query(query, variables=None):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    try:
        response = requests.post(ENDPOINT, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"خطأ في الاتصال: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"حدث استثناء: {e}")
        return None
