from scripting import process
#import consul
import os
import json
import logging
import requests
logging.basicConfig(level=logging.DEBUG)
from templates import frontend

basepath='/www/dmf24.dev.orchestraweb.med.harvard.edu/docroot/lsfportmapper'

server="http://ritglapp02.orchestra:5000"
server_query="/api/all_maps"
TOKEN='TEST'

def lsfparsehost(hoststring):
    def stripcores(hs):
        if '*' in hs:
            return hs.split('*')[1]
        else:
            return hs
    hosts=[stripcores(h) for h in hoststring.split(':')]
    if len(hosts) > 1:
        return hosts
    else:
        return hosts[0]

def jobkey(jd):
    return "%s-%s" % (jd['user'], jd['jobid'])

def ep(host, port):
    return "%s:%s" % (host, port)

def splitep(endpoint):
    ee=endpoint.split(':')
    return (ee[0], int(ee[1]))

class Registry(set):
    def __init__(self, data=set([])):
        self.update(data)
        self.port_range=[9000, 10000]
    def setport(self, host, port, jobdata):
        self.add((jobkey(jobdata), ep(host, port)))
    def registerport(self, host, port, jobdata):
        endpoint=ep(host, port)
        if endpoint not in [item[1] for item in self]:
            self.setport(host, port, jobdata)
        else:
            logging.debug("%s:%s is already registered: %s" % (host, port, endpoint))
            return None
    def next_port(self, host):
        already_registered=[splitep(endpoint)[1] for (name, endpoint) in self if endpoint.startswith(host)]
        for p in xrange(*self.port_range):
            if p not in already_registered:
                return p
        logging.error("No free ports on host: %s" % host)
        return None
    def register(self, jobdata):
        if jobdata['state'] != 'RUN':
            logging.error("Job must be running to register port")
            return None
        host=lsfparsehost(jobdata['exec_host'])
        if isinstance(host, list):
            logging.error("Multi-node jobs not supported: %s" % jobdata)
            return None
        port=self.next_port(host)
        self.registerport(host, port, jobdata)
    def search(self, query):
        ports=[]
        if isinstance(query, str):
            for item in self:
                if query in item[0] or query in item[1]:
                    ports.append(item)
        return ports

def server_get_all():
    response=requests.get(url)
    return set([tuple(x) for x in response.json()])

def server_add(name, endpoint):
    response=requests.post("%s/api/add_map" % server, json=dict(name=name,
                                                                endpoint=endpoint,
                                                                token=TOKEN))
    return response

def server_del(name=None, endpoint=None):
    if name is None and endpoint is None:
        return False
    response=requests.post("%s/api/del_map" % server, json=dict(name=name,
                                                                endpoint=endpoint,
                                                                token=TOKEN))
    return response

def server_update_all(registry):
    response=requests.post("%s/api/replace_all" % server, json=dict(registry=[list(x) for x in registry],
                                                                    token=TOKEN))
    return response
    

def load_registry(url=None):
    if url is not None:
        response=requests.get(url)
        return Registry(set([tuple(x) for x in response.json()]))
    else:
        return Registry()

def parsebj(line):
    items=[x.strip() for x in line.split()]
    if len(items) < 6:
        return []
    #ignore from_host (items[4]) we don't care about where it came from.
    return dict(jobid=items[0],
                user=items[1],
                state=items[2],
                queue=items[3],
                exec_host=items[5])



def bjobsuallw():
    results=process('bjobs -u all -w')
    return [parsebj(line) for line in results[1].split('\n') if line.strip() != '']

def pathname(jobdata, basepath=basepath):
    print jobdata
    return os.path.join(basepath, "{user}/{jobid}".format(**jobdata))

if __name__ == '__main__':
    server_registry=load_registry("%s%s" % (server, server_query))
    registry=Registry()
    from pprint import pprint
    import random
    for j in bjobsuallw():
        if j['user'] in ['dmf24'] and j['state'] == 'RUN':
            if isinstance(lsfparsehost(j['exec_host']), str):
                registry.register(j)
    delete_from_server=server_registry.difference(registry)
    add_to_server=registry.difference(server_registry)
    if len(delete_from_server) < 10:
        logging.debug("delete\n%s" % delete_from_server)
    else:
        logging.debug("deleting %s entries" % len(delete_from_server))
    if len(add_to_server) < 10:
        logging.debug("add\n%s" % add_to_server)
    else:
        logging.debug("adding %s entries" % len(add_to_server))
    if len(delete_from_server) > 0 or len(add_to_server) > 0:
        server_update_all(registry)
