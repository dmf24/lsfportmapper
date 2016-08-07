
# OO programming is so fucking verbose.
class Registry(dict):
    def __init__(self, data={}):
        self.update(data)
        self.port_range=[9000, 10000]
    def setport(self, host, port, jobdata):
        self.setdefault("%s:%s" % (host, port), jobdata)
    def makekey(self, host, port):
        return '%s:%s' % (host, port)
    def splitkey(self, key):
        s=key.split(':')
        return (s[0], int(s[1]))
    def gethp(self, host, port):
        return self.get(self.makekey(host, port), None)
    def registerport(self, host, port, jobdata):
        key=self.makekey(host, port)
        if key not in self.keys():
            self.setport(host, port, jobdata)
        else:
            logging.debug("%s:%s is already registered: %s" % (host, port, self[key]))
            return None
    def next_port(self, host):
        for p in xrange(*self.port_range):
            if self.gethp(host, p) is None:
                return p
        logging.warning("No free ports on host: %s" % host)
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
    def find_ports(self, jobdata):
        ports=[]
        if isinstance(jobdata, dict):
            for hp in self.keys():
                tst=self[hp]
                if False not in [tst[k]==jobdata[k] for k in jobdata.keys()]:
                    ports.append(hp)
        elif isinstance(jobdata, str):
            for hp in self.keys():
                tst=self[hp]
                if True in [jobdata in tst[k] for k in tst.keys()]:
                    ports.append(hp)
        return ports
