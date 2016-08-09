from flask import Flask, request, jsonify
app = Flask(__name__)

import copy
import json
import os
import logging
from pymongo import MongoClient
logging.basicConfig(level=logging.INFO)

from datastore import load_portmap, store_portmap

portmap = load_portmap()
last_portmap = copy.deepcopy(portmap)

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

@app.route("/api/get_endpoint/<jobid>", methods=['GET'])
def get_endpoint(jobid):
    endpoints=[endpoint for name, endpoint in portmap if name.split('-')[1]==jobid]
    if len(endpoints) == 1:
        return endpoints[0]
    elif len(endpoints) == 0:
        return jsonify(False)
    else:
        return jsonify(endpoints)

@app.route("/api/dump_portmap", methods=['GET'])
def dump_portmap():
    return jsonify(list(portmap))

#@app.route("/api/sync_nginx", methods=['GET', 'POST'])
#def sync_nginx():
#    write_nginx_conf(portmap)
#    return jsonify(service_nginx_restart())
#
#@app.route("/api/sync_dns", methods=['GET', 'POST'])
#def sync_dns():
#    return jsonify(updateDNS(portmap, domain))

@app.route("/api/all_maps", methods=['GET'])
def all_maps():
    return jsonify(list(portmap))

# Initiate
doStuffStart()
# When you kill Flask (SIGTERM), clear the trigger for the next thread
atexit.register(interrupt)

if __name__ == "__main__":
    app.run()
