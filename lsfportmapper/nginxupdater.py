from flask import Flask, request, jsonify
app = Flask(__name__)

from templates import frontend
import copy
import json
import threading
import atexit
from scripting import process
import os
import logging
logging.basicConfig(level=logging.INFO)

nginx_portmap_file="/etc/nginx/conf.d/lsfportmap.conf"
nginx_restart_cmd="/sbin/service nginx restart"
cache_file="/var/lsfportmap/data/cache.json"

def load_portmap(fpath=cache_file):
    return set([tuple(x) for x in json.loads(file(fpath).read())])

portmap = load_portmap(cache_file) if os.path.isfile(cache_file) else set([])
last_portmap = copy.deepcopy(portmap)
# variables that are accessible from anywhere

POLL_TIME = 2 #Seconds

# lock to control access to variable
dataLock = threading.Lock()
# thread handler
updater_thread = threading.Thread()

def interrupt():
    global updater_thread
    updater_thread.cancel()

def doStuff():
    global portmap
    global last_portmap
    global updater_thread
    restart_nginx=False
    with dataLock:
        if last_portmap != portmap:
            nginx_site_conf='\n'.join([frontend.render(endpoint=endpoint, name=name)
                                       for name, endpoint in portmap])
            with open(nginx_portmap_file, 'w') as f:
                f.write(nginx_site_conf)
            restart_nginx=True
            with open(cache_file, 'w') as f2:
                f2.write(json.dumps(list(portmap)))
            last_portmap = copy.deepcopy(portmap)
    if restart_nginx:
        results=process('/sbin/service nginx restart')
        if results[0] == 0:
            logging.info(results[1])
        else:
            logging.error(results[2])
    # Set the next thread to happen
    updater_thread = threading.Timer(POLL_TIME, doStuff, ())
    updater_thread.start()   

def doStuffStart():
    global updater_thread
    #start thread
    updater_thread = threading.Timer(POLL_TIME, doStuff, ())
    updater_thread.start()

AUTHORIZED=['TEST']

@app.route("/api/add_map", methods=['GET', 'POST'])
def add_map():
    content=request.json
    token=content['token']
    #name="%s-%s" % (content['user'], content['jobid'])
    #endpoint="%s:%s" % (content['host'], content['port'])
    endpoint=content['endpoint']
    name=content['name']
    if content['token'] in AUTHORIZED:
        with dataLock:
            portmap.add((name, endpoint))
    return jsonify(True)

@app.route("/api/del_map", methods=['GET', 'POST'])
def del_map():
    content=request.json
    endpoint=content.get('endpoint', None)
    name=content.get('name', None)
    if name is None and endpoint is None:
        if 'user' in content.keys() and 'jobid' in content.keys():
            name = "%s-%s" % (content['user'], content['jobid'])
    if content.get('token', None) in AUTHORIZED:
        item=None
        if endpoint is not None:
            items=[x for x in portmap if x[1] == endpoint]
            if len(items) == 1:
                item=items[0]
        elif name is not None:
            items=[x for x in portmap if x[0] == name]
            if len(items) == 1:
                item=items[0]
        if item is not None:
            with dataLock:
                portmap.remove(item)
            return jsonify(True)
    return jsonify(False)

@app.route("/api/all_maps", methods=['GET'])
def all_maps():
    return jsonify(list(portmap))

# Initiate
doStuffStart()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)

if __name__ == "__main__":
    app.run()
