from templates import frontend
import copy
from scripting import process
import os
import logging
import time
from pymongo import MongoClient
logging.basicConfig(level=logging.INFO)
from datastore import load_portmap
from config import domain

POLL_TIME = 5 #Seconds

nginx_portmap_file="/etc/nginx/conf.d/lsfportmap.conf"
nginx_restart_cmd="/sbin/service nginx restart"

portmap = load_portmap()
last_portmap = set([]) #copy.deepcopy(portmap)
# variables that are accessible from anywhere

def write_nginx_conf(portmap):
    logging.info("Writing conf: %s" % nginx_portmap_file)
    nginx_site_conf='\n'.join([frontend.render(endpoint=endpoint, name=name, domain=domain)
                               for name, endpoint in portmap])
    with open(nginx_portmap_file, 'w') as f:
        f.write(nginx_site_conf)                            

def service_nginx_restart():
    logging.info("Restarting nginx")
    results=process('/sbin/service nginx restart')
    if results[0] == 0:
        logging.info(results[1])
        return True
    else:
        logging.error(results[2])
        return False

def check_and_restart():
    global portmap
    global last_portmap
    portmap=load_portmap()
    if last_portmap != portmap:
        write_nginx_conf(portmap)
        service_nginx_restart()
        last_portmap = copy.deepcopy(portmap)

if __name__ == "__main__":
    while True:
        check_and_restart()
        time.sleep(POLL_TIME)
