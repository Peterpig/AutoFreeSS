# -*- coding:utf-8 -*-

import pprint
import json
import threading
import time
import os
import subprocess
import requests
from lxml import etree

path = os.getcwd()
file_name = 'gui-config.json'

def get_config():
    ss_url = 'http://freevpnss.cc/'

    req = requests.get(ss_url)
    html_content = req.content.decode('utf-8')
    page = etree.HTML(html_content)

    root_list = page.xpath(u'//div[@id="shadowsocks"]/following::*')

    ret_config = '''{'''
    configs = []

    for root in root_list:
        ss_box = root.xpath('.//div[@class="col-sm-4"]')
        for ss in ss_box:
            title = ss.xpath('.//h3[@class="panel-title"]')[0].text
            address = ss.xpath('.//div[@class="panel-body"]/p[1]')[0].text
            port = ss.xpath('.//div[@class="panel-body"]/p[2]')[0].text
            password = ss.xpath('.//div[@class="panel-body"]/p[3]/span/following::node()')[0]
            method = ss.xpath('.//div[@class="panel-body"]/p[4]')[0].text

            configs.append({
                "remarks": title,
                "server": address.split('：')[1],
                "server_port": port.split('：')[1],
                "password": password.split('：')[1],
                "method": method.split('：')[1].lower(),
            })
    return configs

def writ_config(configs):
    with open(file_name, 'w') as f:
        f.write('{ "configs": ')
        f.write(json.dumps(configs, sort_keys=True, indent=4))
        f.write(',')
        f.write('''
            "index" : 1,
            "random" : false,
            "global" : false,
            "enabled" : true,
            "shareOverLan" : false,
            "isDefault" : false,
            "bypassWhiteList" : false,
            "localPort" : 1080,
            "reconnectTimes" : 0,
            "randomAlgorithm" : 0,
            "TTL" : 0,
            "proxyEnable" : false,
            "pacDirectGoProxy" : false,
            "proxyType" : 0,
            "proxyHost" : null,
            "proxyPort" : 0,
            "proxyAuthUser" : null,
            "proxyAuthPass" : null,
            "authUser" : null,
            "authPass" : null,
            "autoBan" : false,
            "sameHostForSameTarget" : false
        ''')
        f.write('}')

def get_new_config_file():
    configs = get_config()
    writ_config(configs)

def configs_to_dict(configs):
    ret = {}
    for config in configs:
        ret[config['server']] = config
    return ret

def get_now_config():
    if not os.path.exists(file_name):
        get_new_config_file()

    with open(file_name, 'r') as f:
        config = json.loads(f.read())
        return config['configs']

def auto_sync_config():
    new_configs = configs_to_dict(get_config())
    old_configs = configs_to_dict(get_now_config())

    try:
        for server, config in new_configs.items():
            new_pass = new_configs[server]['password']
            old_pass = old_configs[server]['password']
            if new_pass != old_pass:
                get_new_config_file()
                break
    except:
        get_new_config_file()

    app_restart()

def kill_exe():
    p = subprocess.Popen(["tasklist"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    killlist = ['ssr_privoxy.exe', 'ShadowsocksR-dotnet4.0.exe', 'ShadowsocksR-dotnet2.0.exe', 
                'ShadowsocksR-dotnet4.0.ex', 'ShadowsocksR-dotnet2.0.ex']
    for line in out.splitlines():
        try:
            line = bytes.decode(line)
            im = line.split()[0]
            if im in killlist:
                pid = line.split()[1]
                os.system("taskkill /F /PID " + pid)
        except:
            continue

def start_exe():
    files = '%s/ShadowsocksR-dotnet4.0.exe' % path
    os.startfile(files)

def app_restart():
    kill_exe()
    start_exe()

def timer_start():
    auto_sync_config()
    t = threading.Timer(3000, timer_start)  
    t.start()

if __name__ == "__main__":  
    timer_start()
