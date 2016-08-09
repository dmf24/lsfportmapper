from pymongo import MongoClient
import logging

dburl='mongodb://localhost:27017/'
pmquery=dict(name='portmap')
initial=dict(name='portmap', portmap=[])

def load_portmap():
    coll=MongoClient(dburl).lsfportmap.lsfportmap
    ppm = coll.find_one(pmquery)
    if ppm is None:
        item=coll.insert_one(initial)
    pm = coll.find(pmquery)
    if pm is not None:
        if pm.count() != 1:
            logging.warning("multiple portmaps found")
        return set(pm[0]['portmap'])

def dump_portmap():
    return set(MongoClient(dburl).lsfportmap.lsfportmap.find_one(pmquery)['portmap'])

def store_portmap(pm):
    coll=MongoClient(dburl).lsfportmap.lsfportmap
    return coll.replace_one(pmquery, {'name': 'portmap',
                                      'portmap': list(pm)})

if __name__ == '__main__':
    import sys
    import json
    sys.stdout.write("%s\n" % json.dumps(load_portmap(), indent=2))
