#!/usr/bin/env python3
# author: suanve
import requests
import multiprocessing
import argparse
import re
import itertools
import sys
import IPy
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# multiprocessing.set_start_method('spawn', True)

GetIp = lambda x: ["%d.%d.%d.%d" % d for d in itertools.product(
    *[range(m, n + 1) for s in x.split(".") for m, n, *_ in [map(int, (s + "-" + s).split("-"))]])]

portList = [
    80, 81, 88, 808, 888, 8000,8008, 8080,8001, 8888, 8020,8009,8081,8082,8083
]


def checkIp(ip):
    if re.compile(r"^\d+\.\d+\.\d+\.\d+$").match(ip):
        ip = ip.split('.')
        hosts = []
        for tmpI in range(255):
            ip[-1] = str(tmpI)
            hosts.append(".".join(ip))
        return hosts

    if re.compile(r"^\d+\.\d+\.\d+\.\d+/\d+$").match(ip):
        hosts = []
        [hosts.append(str(s)) for s in IPy.IP(ip)]
        return hosts

    if re.compile(r"^\d+\.\d+\.\d+\.\d+-\d+$").match(ip):
        return GetIp(ip)

def getTitle(host, port):
    s = requests.session()
    url = f"http://{host}:{port}"
    res = s.get(url, timeout=3)
    title = re.findall(r'<title>(.*?)</title>', res.text)[0]
    print(f"[*] {res.status_code} {url} {title}")

def getAddress(domain):
    if domain[0:7] != "http://":
        url = f"http://{domain}"
    try:
        s = requests.session()
        s.headers[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        res = s.get(url, timeout=5, stream=True, verify=False)
        try:
            address = res.raw._connection.sock.getpeername()[0]
        except AttributeError:
            exit("未获取到ip")
    except:
        pass


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        exit(f"[-] {sys.argv[0]} 172.16.101.9-254 20\n[-] {sys.argv[0]} 范围 线程")

    try:
        hosts = checkIp(sys.argv[1])
    except:
        exit(f"[-] {sys.argv[0]} 172.16.101.9-254 20\n[-]{sys.argv[0]} 范围 线程")

    try:
        if int(sys.argv[2]) not in range(1, 201): raise 1
    except:
        processesNum = 20
        print(f"[-]{sys.argv[0]} 线程设置错误或未设置,默认为20")
    else:
        processesNum = int(sys.argv[2])

    pool = multiprocessing.Pool(processes=processesNum)
    for host in hosts:
        for port in portList:
            pool.apply_async(getTitle, (host, port))

    pool.close()
    pool.join()