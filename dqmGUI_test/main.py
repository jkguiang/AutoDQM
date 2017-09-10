import sys

def main(args):
    query = args
    timestamp = 0
    status = "succes"
    fail_reason = None
    warning = None
    payload = args
    return json.dumps( { "query": query, "timestamp": timestamp, "response": { "status": status, "fail_reason": fail_reason, "warning": warning, "payload": payload } } )

if __name__ == "__main__":
    print(main(args))
