import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def test_delete(member_id):
    url = f'http://127.0.0.1:8000/api/members/{member_id}/delete/'
    req = urllib.request.Request(url, method='POST')
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            print(r.status, r.read().decode())
    except Exception as e:
        print(f"Error {member_id}:", str(e))

# get members of family 5611
url = f'http://127.0.0.1:8000/api/families/5611/members/'
req = urllib.request.Request(url, method='GET')
try:
    with urllib.request.urlopen(req, context=ctx) as r:
        dat = json.loads(r.read().decode())
        print(dat)
        if dat:
            member = dat[0]['id']
            print("Deleting member", member)
            test_delete(member)
except Exception as e:
    print(e)
