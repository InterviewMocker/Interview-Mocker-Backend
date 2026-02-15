import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_sse_extraction():
    print("🚀 Starting SSE Extraction Test...")
    
    # 1. Login to get token
    username = "auth_test_user_01"
    password = "TestUser123!"
    
    print(f"\n1. Logging in as {username}...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        if resp.status_code != 200:
            print(f"❌ Login failed: {resp.text}")
            return
        token = resp.json()['data']['access_token']
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return

    # 2. Get a valid bank ID (or create one)
    print(f"\n2. Getting/Creating a question bank...")
    headers = {"Authorization": f"Bearer {token}"}
    bank_id = None
    try:
        # List banks
        resp = requests.get(f"{BASE_URL}/questions/banks", headers=headers)
        if resp.status_code == 200 and resp.json()['data']['items']:
            bank_id = resp.json()['data']['items'][0]['id']
            print(f"✅ Found existing bank: {bank_id}")
        else:
            # Create bank
            print("Creating new bank...")
            resp = requests.post(f"{BASE_URL}/questions/banks", headers=headers, json={
                "name": "SSE Test Bank",
                "description": "For testing streaming extraction",
                "status": "active"
            })
            if resp.status_code == 200:
                bank_id = resp.json()['data']['id']
                print(f"✅ Created new bank: {bank_id}")
            else:
                print(f"❌ Failed to create bank: {resp.text}")
                return
    except Exception as e:
        print(f"❌ Bank operation failed: {e}")
        return

    # 3. Upload file and stream response
    print(f"\n3. Uploading file and listening for SSE...")
    
    # Create a dummy text file content
    file_content = """
    Question 1: What is Python?
    Answer: Python is a high-level programming language.
    Key points: Readable, Interpreted, Dynamic typing.
    
    Question 2: Explain GIL in Python.
    Answer: Global Interpreter Lock.
    Key points: Mutex, Thread-safety, CPython.
    
    Question 3: What is a decorator?
    Answer: A function that takes another function and extends its behavior.
    Key points: Higher-order function, @syntax, Wrappers.
    """
    
    files = {
        'file': ('test_questions.txt', file_content, 'text/plain')
    }
    data = {'bank_id': bank_id}
    
    try:
        start_time = time.time()
        last_event_time = start_time
        
        with requests.post(
            f"{BASE_URL}/questions/extract",
            headers=headers,
            files=files,
            data=data,
            stream=True,
            timeout=60
        ) as response:
            if response.status_code != 200:
                print(f"❌ Extraction failed: {response.status_code} - {response.text}")
                return

            print("✅ Connection established. Receiving events...")
            
            client = requests.Session() # dummy
            
            # Simple SSE line parser
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('event:'):
                        event_type = decoded_line[6:].strip()
                        current_time = time.time()
                        time_diff = current_time - last_event_time
                        last_event_time = current_time
                        print(f"\n[+{time_diff:.2f}s] Event: {event_type}")
                    elif decoded_line.startswith('data:'):
                        data_str = decoded_line[5:].strip()
                        try:
                            data_json = json.loads(data_str)
                            if 'new_questions' in data_json:
                                qs = data_json['new_questions']
                                print(f"  -> Received {len(qs)} question(s): {[q['title'] for q in qs]}")
                            elif 'total_questions' in data_json:
                                print(f"  -> Completed. Total: {data_json['total_questions']}")
                        except:
                            print(f"  -> Data: {data_str[:50]}...")
                            
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        return

    print("\n🎉 SSE Test Completed!")

if __name__ == "__main__":
    test_sse_extraction()
