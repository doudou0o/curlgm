#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
from urlparse import urlparse
import json
import re
from gearman import GearmanClient
import msgpack
import time

class gm_req:
    def __init__(self):
        self.IP = None
        self.port = None
        self.worker = None
        self.request = None
        self.header = None
        self.params = None

    def show(self):
        print "your gearman request:"
        print "IP= " + self.IP
        print "worker=" + str(self.worker)
        print "header=" + str(self.header)
        print "request=" + str(self.request)
        if self.params:
            print "params=" + str(self.params)

Header_gl = None

def curlgm_encode(strline):
    matches = re.finditer("\".*?\"", strline)
    change_pos_list = []
    for m in matches:
        s,e = m.start(), m.end()
        newstr = strline[s:e]
        newstr = re.sub("=","\=",newstr)
        newstr = re.sub("&","\&",newstr)
        change_pos_list.append([s,e,newstr])
    change_pos_list.reverse()
    for f in change_pos_list:
        s,e,newstr = f
        strline = strline[:s]+newstr+strline[e:]
    return strline
def curlgm_decode(strline):
    strline = re.sub("\\\\&", "&" ,strline)
    strline = re.sub("\\\\=", "=" ,strline)
    return strline

def parse_value(value):
    if value.startswith("\"") and value.endswith("\""):
        return curlgm_decode(value[1:-1].decode("utf8"))
    try:
        if re.search("\.", value):
            value_num = float(value)
        else:
            value_num = int(value)
        return value_num
    except:
        pass
    if value.startswith("{") and value.endswith("}"):
        value = curlgm_decode(value)
        return json.loads(value)
    if value.startswith("[") and value.endswith("]"):
        value = curlgm_decode(value)
        return json.loads(value)

    return curlgm_decode(value.decode("utf8"))

def parse_param(params):
    if not params:
        return ""
    params = curlgm_decode(params)
    paramMap = {}
    params = params.split(";")
    for para in params:
        if not para: continue
        f = para.split("=")
        if len(f) != 2: continue
        paramMap[f[0].strip()] = f[1].strip()
        if f[0] == "para":
            paramMap["para"] = [ v.strip() for v in f[1].split(",") ]

    return paramMap

def parse_request(request, params_dict):
    request = curlgm_encode(request)
    requestMap = {}
    reqs = re.split("(?<!\\\\)&&", request)
    if len(reqs) != len(params_dict["para"]):
        print "err! num of reqs and para are diff"

    for i, req in enumerate(reqs):
        if not re.search("(?<!\\\\)=", req):
            requestMap[params_dict["para"][i]] = parse_value(req)
            continue
        requestMap[params_dict["para"][i]] = {}
        sub_reqs = re.split("(?<!\\\\)&", req)
        for pair in sub_reqs:
            f = re.split("(?<!\\\\)=", pair)
            if len(f) != 2: continue
            k,v = parse_value(f[0].strip()), parse_value(f[1].strip())
            requestMap[params_dict["para"][i]][k] = v
    return requestMap

def parse(url_res):
    url_res.port   = str(url_res.port)
    url_res.header = auto_header() if not Header_gl else Header_gl
    url_res.params = parse_param(url_res.params)
    url_res.request = parse_request(url_res.request, url_res.params)
    return url_res

def auto_header():
    import socket
    import getpass
    localIP = socket.gethostbyname(socket.gethostname())
    user = getpass.getuser()

    header={}
    header["user_name"] = user
    header["user_ip"] = localIP
    header["product_name"] = "curlgm"
    return header

def send_request(req):
    new_client = GearmanClient([req.IP])

    s = time.time()
    request_dict={}
    request_dict["header"] = req.header
    request_dict["request"]= req.request
    if "pack_in" in req.params and req.params["pack_in"] == "0":
        current_request = new_client.submit_job(req.worker,request_dict)
    else:
        current_request = new_client.submit_job(req.worker,msgpack.packb(request_dict))

    if "pack_out" in req.params and req.params["pack_out"] == "0":
        current_result = current_request.result
    else:
        current_result = msgpack.unpackb(current_request.result)
    e = time.time()
    print "using time:%f" % (e-s)

    return current_result

def url_convect(url):
    res = gm_req()
    try:
        o = urlparse(url)
        res.IP = o.netloc
        res.port = o.port
        res.worker = re.sub("^/","",o.path)
        res.params = o.params #TODO need clean
        res.request = o.query #TODO need clean
    except Exception as e:
        print "can not parse url"
        print e
    return res


def set_global_header(filepath):
    global Header_gl
    try:
        Header_gl = json.load(open(filepath,"r"))
    except Exception as err:
        print err
        print "some problem occured in HeaderFile! and will use AutoHeader"
        Header_gl = None
def rollfile(filepath, isInfo, isTest):
    with open(filepath,"r") as fp:
        i = 0
        for line in fp:
            i+=1;print "line#%d" % i
            url = line.strip()
            # convect info
            url_result = url_convect(url)
            if not url_result.IP:
                url_result.IP = raw_input("please enter worker IP: ")
            if not url_result.port:
                url_result.port = raw_input("please enter port: ")
            if not url_result.worker:
                url_result.worker = raw_input("please enter worker name: ")

            # parse info
            req = parse(url_result)
            if isInfo:
                print "---------"
                req.show()
                print "---------"

            if isTest: continue
            # send gm req
            res = send_request(req)
            print json.dumps(res, ensure_ascii=False)
    pass
def usage():
    print "./curlgm gm_url [-i -t][--conf headerfile --file inputfile]\nFor more details, please read the readme.md"
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htic:f:", ["help", "test","info","conf=","file="])
    except getopt.GetoptError as err:
        print err;usage();sys.exit(2)
    isTest, isInfo=False, False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage();sys.exit()
        if o in ("-c", "--conf"):
            set_global_header(a)
        if o in ("-i", "--info"):
            isInfo = True
        if o in ("-t", "--test"):
            isTest = True
        if o in ("-f", "--file"):
            rollfile(a,isInfo,isTest);sys.exit()
    if len(args) < 1: print "missing args";  sys.exit()
    if len(args) > 1: print "too much args"; sys.exit()
    url = args[0]

    # convect info
    url_result = url_convect(url)
    if not url_result.IP:
        url_result.IP = raw_input("please enter worker IP: ")
    if not url_result.port:
        url_result.port = raw_input("please enter port: ")
    if not url_result.worker:
        url_result.worker = raw_input("please enter worker name: ")

    # parse info
    req = parse(url_result)
    if isInfo:
        print "---------"
        req.show()
        print "---------"

    if isTest: sys.exit()
    # send gm req
    res = send_request(req)
    print json.dumps(res, ensure_ascii=False)




