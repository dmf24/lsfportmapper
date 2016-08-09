import boto
import boto.route53
import requests
import logging
import os
import copy
from datastore import load_portmap
from config import domain, canonical_name

lockfile_path="/var/run/dnsupdater.lock"

portmap=load_portmap()
last_portmap=copy.deepcopy(portmap)


def dnstest():
    import boto.route53
    conn = boto.route53.connect_to_region('us-west-2')
    zname='orchestra-cluster.dougfeldmann.com'
    zone=conn.get_zone(zname)
    
    return (zone, [x for x in zone.get_records() if x.name != "%s." % zname])

def exceptor(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except:
        import sys
        logging.error(sys.exc_info())
        return sys.exc_info()

def updateDNS(portmap, domain, canonical_name):
    conn = boto.route53.connect_to_region('us-west-2')
    if conn is None:
        logging.error(boto.config.dump())
        return None
    zone=conn.get_zone(domain)
    records=dict([(gethname(x), x) for x in zone.get_records() if x.type == u'CNAME'])
    indns=set(records.keys())
    current_names=set([name for name,endpoint in portmap])
    records_to_delete=indns.difference(current_names)
    records_to_add=current_names.difference(indns)
    for rr in records_to_delete:
        exceptor(zone.delete_cname, records[rr].name)
    for rr in records_to_add:
        exceptor(zone.add_cname, '.'.join([rr, domain]), canonical_name, ttl=10)
    return True

def check_and_update():
    portmap=load_portmap()
    if last_portmap != portmap:
        updateDNS(portmap, domain, canonical_name)
        service_nginx_restart()
        last_portmap = copy.deepcopy(portmap)

if __name__ == '__main__':
    while True:
        check_and_update()
        time.sleep(dnsupdater_poll_time)
