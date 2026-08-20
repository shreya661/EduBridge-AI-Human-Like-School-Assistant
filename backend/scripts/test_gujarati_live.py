import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import urllib.parse
import json

def test_flow(user_id, queries, lang='gu'):
    print(f"=== Testing {user_id} with Language: {lang} ===")
    login_data = json.dumps({'user_id': user_id}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=login_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        cookie = resp.headers.get('Set-Cookie')
        user_info = json.loads(resp.read().decode('utf-8'))
        print(f"User: {user_info['user']['name']} ({user_info['user']['role']})")

    for q in queries:
        params = urllib.parse.urlencode({'text': q, 'language': lang})
        req = urllib.request.Request(f'http://127.0.0.1:8000/api/v1/nlu/execute?{params}', headers={'Cookie': cookie}, method='POST')
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print(f"  Query: \"{q}\"")
            print(f"  Response: {res.get('message')}\n")

if __name__ == '__main__':
    # 1. Student (S001)
    test_flow('S001', ['મારી હાજરી શું છે?', 'નમસ્તે'], 'gu')

    # 2. Parent (P001)
    test_flow('P001', ['મારા બાળકની હાજરી કેટલી છે?', 'રાહુલની હાજરી કેવી છે?'], 'gu')

    # 3. Teacher (T001)
    test_flow('T001', ['રાહુલને આજે ગેરહાજર માર્ક કરો'], 'gu')
