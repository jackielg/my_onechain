# coding=utf-8

import configparser
import logging
import os
import re
import time
import requests
import json
import urllib

# 日志
# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关

# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
logfile = 'new.log'
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.WARNING)  # 输出到file的log等级的开关

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)  # 输出到console的log等级的开关

# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

ch.setFormatter(formatter)
logger.addHandler(ch)


# logger.debug('this is a logger debug message')
# logger.info('this is a logger info message')
# logger.warning('this is a logger warning message')
# logger.error('this is a logger error message')
# logger.critical('this is a logger critical message')

# start
logging.warning('***** Start ...')
curpath = os.getcwd()

# get config information
content = open(curpath + '/config.ini').read()
content = re.sub(r"\xfe\xff", "", content)
content = re.sub(r"\xff\xfe", "", content)
content = re.sub(r"\xef\xbb\xbf", "", content)
open(curpath + '\config.ini', 'w').write(content)

cf = configparser.ConfigParser()
cf.read(curpath + '\config.ini')
user_agent = cf.get('info', 'user_agent').strip()
device_id = cf.get('info', 'device_id').strip()
l = cf.get('info', 'l').strip()
# token = cf.get('info', 'token').strip()
version = cf.get('info', 'version').strip()

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'User-Agent': 'OneChainIOS/1.2.4 (iPhone; iOS 11.3; Scale/3.00)',
    'Accept-Language': 'zh-Hans-CN;q=1',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Length': '151'
}



def loginGetAccessToken(user_agent, device_id, l, version):
    url_login = 'http://hkopenservice1.yuyin365.com:8000/one-chain/login?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=&version=' + version


    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_login, data=data, headers=headers)

        # if bProxy == 0:
        #     r = requests.post(url_login, headers=headers, verify=False) #headers=headers,
        # else:
        #     r = requests.post(url_login, headers=headers, proxies=proxies, verify=False) #headers=headers,

        res = r.json()["msg"]
        if res == 'Success':
            token = r.json()["data"]["map"]["token"]
            return token
        else:
            return -1
    except Exception as e:
        print(e)
        return -1

def open_mining(user_agent, device_id, l, token, version):
    url_check = 'http://hkopenservice1.yuyin365.com:8000/one-chain/mining/start?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=' + token + '&version=' + version

    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_check, data=data, headers=headers)

        res = r.json()["msg"]
        if res == 'Success':
            logging.warning('>>>>>>>>>> mining_opened.')
            return 0
        else:
            return -1

    except Exception as e:
        print(e)
        return


def get_calculated(user_agent, device_id, l, token, version):
    url_check = 'http://hkopenservice1.yuyin365.com:8000/one-chain/mining/user/infoString?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=' + token + '&version=' + version

    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_check, data=data, headers=headers)

        res = r.json()["msg"]
        if res == 'Success':
            mining_flag = r.json()['data']['map']['mining_flag']
            if mining_flag == "NO":
                open_mining(user_agent, device_id, l, token, version)
                logging.warning('>>>>>>>>>> mining opened')

            calculated = r.json()['data']['map']['calculated']
            logging.warning('>>>>>>>>>> calculated: ' + calculated)
    except Exception as e:
        print(e)
        return


def mining_click(user_agent, device_id, l, token, version, mining_detail_uuid):
    url_check = 'http://hkopenservice1.yuyin365.com:8000/one-chain/mining/detail/click?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=' + token + '&version=' + version + '&mining_detail_uuid=' + mining_detail_uuid

    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_check, data=data, headers=headers)

        res = r.json()["msg"]
        if res == 'Success':
            logging.warning('>>>>>>>>>> mining...... ' + str(mining_detail_uuid))
            return 0
        else:
            return -1
    except Exception as e:
        print(e)
        return


def mining_check(user_agent, device_id, l, token, version):
    url_check = 'http://hkopenservice1.yuyin365.com:8000/one-chain/mining/detail/list?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=' + token + '&version=' + version

    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_check, data=data, headers=headers)

        res = r.json()["msg"]
        if res == 'Success':
            contentlist = r.json()['data']['list']
            i = 0
            for i in range(len(contentlist)):
                uni_uuid = contentlist[i]['uni_uuid']
                mining_click(user_agent, device_id, l, token, version, str(uni_uuid))

            if i == 0:
                logging.warning('>>>>>>>>>> mining_clicked: ' + str(i))
            else:
                logging.warning('>>>>>>>>>> mining_clicked: ' + str(i+1))
            return 0
        else:
            return -1

    except Exception as e:
        print(e)
        return

def check_allTotal(user_agent, device_id, l, token, version):
    url_check = 'http://hkopenservice1.yuyin365.com:8000/one-chain/mining/allTotal?user_agent=' + user_agent + '&device_id=' + device_id + '&l=' + l + '&token=' + token + '&version=' + version

    one = 0
    oneluck = 0

    try:
        requests.packages.urllib3.disable_warnings()
        r = requests.post(url_check, data=data, headers=headers)

        res = r.json()["msg"]
        if res == 'Success':
            totallist = r.json()['data']['list']
            i = 0
            for i in range(len(totallist)):
                asset_code = totallist[i]['asset_code']
                total = totallist[i]['total']
                if asset_code == "ONE":
                    one = total
                if asset_code == "ONELUCK":
                    oneluck = total
                logging.warning('>>>>>>>>>> ' + asset_code + ': ' + str(total))
            return one, oneluck
        else:
            return -1, -1

    except Exception as e:
        print(e)
        return -1, -1


def loop_data_mining():

    global data
    global token
    one_total = 0
    oneluck_total = 0

    file = open('one_chain_data.json', 'r', encoding='utf-8')
    data_dict = json.load(file)
    # print(data_dict)
    # print(type(data_dict))

    for item in data_dict['data']:
        account_id= item.get('account_id', 'NA')
        account_name = item.get('account_name', 'NA')
        signed_message = item.get('signed_message', 'NA')

        data=dict(account_id=account_id,account_name=account_name,signed_message=signed_message)

        logging.warning("========== Checking [" + account_name + "] ==========")

        token = loginGetAccessToken(user_agent, device_id, l, version)
        if token == -1:
            logging.warning('********** Login fail!')
            exit(-1)
        else:
            logging.warning('********** Login success! token:' + token)

            get_calculated(user_agent, device_id, l, token, version)
            mining_check(user_agent, device_id, l, token, version)
            (one, oneluck) = check_allTotal(user_agent, device_id, l, token, version)
            one_total = one_total + float(one)
            oneluck_total = oneluck_total + float(oneluck)
            logging.warning("========== End[" + account_name + "], Total[ONE:" + str(one_total) + ", ONELUCK:" + str(oneluck_total)+"] ==========")
            logging.warning('\n')

############ Main #############


loop_data_mining()

