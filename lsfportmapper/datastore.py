from pymongo import MongoClient
import logging

dburl='mongodb://localhost:27017/'
pmquery=dict(name='portmap')
initial=dict(name='portmap', portmap=[])

def pmset(pmq):
    return set([tuple(lst) for lst in pmq['portmap']])

def set2lst(pm):
    return list([list(x) for x in pm])

def load_portmap():
    coll=MongoClient(dburl).lsfportmap.lsfportmap
    ppm = coll.find_one(pmquery)
    if ppm is None:
        item=coll.insert_one(initial)
    pm = coll.find(pmquery)
    if pm is not None:
        if pm.count() != 1:
            logging.warning("multiple portmaps found")
        return pmset(pm[0])

def dump_portmap():
    return pmset(MongoClient(dburl).lsfportmap.lsfportmap.find_one(pmquery))

def store_portmap(pm):
    coll=MongoClient(dburl).lsfportmap.lsfportmap
    return coll.replace_one(pmquery, {'name': 'portmap',
                                      'portmap': set2lst(pm)})

def drop_portmap():
    MongoClient(dburl).lsfportmap.lsfportmap.drop()


if __name__ == '__main__':
    import sys
    import json
    portm=load_portmap()
    sys.stdout.write("%s\n" % json.dumps(list(portm), indent=2))
    sys.stdout.write("%s\n" % len(portm))
