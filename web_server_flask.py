from flask import Flask
from flask import json
from flask import request
from flask import jsonify
from flask_cors import CORS
import redis
import time
import base64

redis_server = redis.StrictRedis.from_url('redis://127.0.0.1:6379/9')

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/close', methods=['POST'])
def close_problem():
    recieved = request.get_json()
    #print("the data:", jsn)
    b64=base64.b64decode(recieved["data"], validate=True)
    b64dec=b64.decode("ascii")
    inp_problem=json.loads(b64dec)
    print("close problem:", inp_problem)
    closing_problem_id=inp_problem["problem_id"]

    the_dic={}
    the_problem=redis_server.hgetall(closing_problem_id)
    print("the problem:", the_problem)

    for key in the_problem:
        print(key.decode("ascii"), the_problem[key].decode("ascii"))
        the_dic[key.decode("ascii")]=str(the_problem[key].decode("ascii"))
    the_dic["state"]="closed"
    print("modified dic:", the_dic)
    redis_server.hmset(closing_problem_id, the_dic)

    ans="close processed"
    return json.dumps(ans)

@app.route('/user_request', methods=['POST'])
def save_problem():
    recieved = request.get_json(force=True)
    print("the data:", recieved)
    #b64=base64.b64decode(recieved["data"], validate=True)
    #b64dec=b64.decode("ascii")
    #inp_json=json.loads(b64dec)

    #print("###:", type(inp_json), inp_json)
    print("###:", type(recieved["data"]), recieved["data"])
    
    the_dic=json.loads(recieved["data"])
    print("###:", type(the_dic), the_dic)
    
    timestamp=str(int(time.time()*1000))
    redis_server.hmset("problem_"+timestamp, the_dic)

    ans="request processed"
    return json.dumps(ans)

@app.route('/show_problems', methods=['GET'])
def show_problems():
    d=redis_server.keys("problem_*")
    resp={}
    for f in d:
        dic={}
        tmp=redis_server.hgetall(f)
        print(tmp)
        for key in tmp:
            print(key.decode("utf8"), tmp[key].decode("utf8"))
            dic[key.decode("utf8")]=str(tmp[key].decode("utf8"))
        resp[f.decode("utf8")]=dic
    print(resp)
    return json.dumps(resp)

@app.route('/remove_element', methods=['POST'])
def remove_element():
    recieved = request.get_json(force=True)
    print("the data:", recieved)
    print("###:", type(recieved["data"]), recieved["data"])
    redis_server.delete(recieved["data"])
    resp={"resp":"ok"}
    return json.dumps(resp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9019, debug=True, ssl_context=('fullchain.pem', 'privkey.pem'))
