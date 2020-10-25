# -*- encoding:utf-8 -*-


import subprocess
import json
import requests
from pprint import pprint
import time

SS_CONFIG_PATH = "/etc/shadowsocks/config.json"
SAVE_SUCCEED_PATH = "succeed.txt"
PROXY_INFO = "real.txt"
FLAG_SUCCEED = "FILE"


def performCommand(server, port, user, password, encrypt_method):

    # 修改配置文件

    server_config = {

        "server": server,
        "server_port": port,
        "local_address": "0.0.0.0",
        "local_port": 1080,
        "password": password,
        "timeout": 300,
        "method": "aes-256-cfb",
        "fast_open": False,
        "workers": 1
    }

    modifyConfig(server_config)

    # 启动客户端代理

    p = subprocess.Popen('/usr/local/bin/sslocal -c {} -d start'.format(SS_CONFIG_PATH), shell=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in p.stdout.readlines():
        print("line:{}".format(line))

    retval = p.wait()
    print("retval:{}".format(retval))

    # 测试代理可用
    if(checkAvailable()):
        p_kill = subprocess.Popen("ps aux | grep sslocal | head -n 1 | awk '{print $2}' | xargs kill", shell=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p_kill.stdout.readlines():
            print("line:{}".format(line))
        retval = p_kill.wait()
        print("retval".format(retval))
        return True
    else:
        return False

    # 结束代理


def do(server, server_port, password):
    checkSatrtKill()

    # server = "123.123.123.123"
    # server_port = 8888
    # password = "abcdefg"
    encrypt_method = "aes-256-cfb"
    if(performCommand(server, server_port, "", password, encrypt_method)):
        treatSucceedProxy(server,server_port,password)
        print("代理可用")
    else:
        print("代理不可用")


def modifyConfig(dicts):
    try:
        js = json.dumps(dicts, indent=4, separators=(',', ':'))
        with open(SS_CONFIG_PATH, 'w') as fw:
            fw.write(js)
    except Exception as e:
        print(e)
        raise



def checkAvailable():
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    try:
        res = requests.get("https://www.google.com",proxies=proxies,timeout=300)
        print("res.status_code:{}".format(res.status_code))
        stcode = res.status_code
        if(stcode == 200):
            return True
    except Exception as e:
        print(e.values)
        return False


def checkSatrtKill():
    # sslocal -c /etc/shadowsocks/config.json -d stop
    p_kill = subprocess.Popen("ps aux | grep sslocal | head -n 1 | awk '{print $2}' | xargs kill", shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p_kill.stdout.readlines():
        print("line:{}".format(line))
    retval = p_kill.wait()
    # print("retval:{}".format(retval))



def getProxyByLocal(p_path):

    # 从本地文件中获取需要测试的代理信息

    with open(p_path) as fr:
        # all_proxy = len(fr.readlines())
        # print("all_work:{}".format(all_proxy))
        for proxyInfos in fr.readlines():
            proxy_info = proxyInfos.split("-")
            if(len(proxy_info)==3):
                proxy_host = proxy_info[0]
                proxy_port = proxy_info[1]
                proxy_password = proxy_info[2].strip('\n').strip('\t')
                do(server=proxy_host, server_port=proxy_port, password=proxy_password)
                time.sleep(3)

    print("[+] done local")


def treatSucceedProxy(host, port, password):
    if (FLAG_SUCCEED == "FILE"):
        path = SAVE_SUCCEED_PATH
        payload = host + "-" + port + "-" + password
        with open(path,'a+') as fw:
            fw.write(payload)
            fw.write("\n")
            fw.flush()
            fw.close()

    elif (FLAG_SUCCEED == "UPLOAD"):
        pass
    else:
        pass


# 运行时检测

def use_proxy(func):
    import socket
    import socks
    import requests

    def wrapper(*args, **kwargs):
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
        socket.socket = socks.socksocket
        print(requests.get('http://ifconfig.me/ip').text)
        return func(*args, **kwargs)

    return wrapper


@use_proxy
def test_proxy():
    import requests
    print(requests.get('http://ifconfig.me/ip').text)
    print 'eacheng'


if __name__ == "__main__":
    # checkSatrtKill()
    # do()
    path = PROXY_INFO
    getProxyByLocal(path)




