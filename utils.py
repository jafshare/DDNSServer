import logging
import time
import re
import random
import yaml
from urllib import request

import chardet

logger = logging.getLogger("ddns")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s:%(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler(filename='ddns.log', mode='a', encoding='utf-8')
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(console)

ip_query_api = [
    "http://{year}.ip138.com/ic.asp".format(year=time.strftime('%Y')),
    "http://www.net.cn/static/customercare/yourip.asp",
    "http://pv.sohu.com/cityjson"
]


def get_ip(retry=3, timeout=10, interval=10):
    """
    根据url获取ip
    :param retry: 最大重试次数
    :param timeout: 超时时间
    :param interval: 重试间隔
    :return: 将获取到的ip返回
    """
    ip = None
    for i in range(retry):
        try:
            url = random.choice(ip_query_api)
            with request.urlopen(url, timeout=timeout) as res:
                ip = parse_ip(res.read())
                if ip:
                    break
        except:
            logger.exception('获取网页数据失败！正在重试(%s/%s)', i+1, retry)
            # 当ip获取失败后的重新获取的间隔
            time.sleep(interval)
            continue
    return ip


def parse_ip(content):
    ip = None
    try:
        # 通过chardet库获取编码
        charset = chardet.detect(content)
        ip_pattern = r"\d{1,3}(\.\d{1,3}){3}"
        ip = re.search(ip_pattern, content.decode(charset['encoding'])).group(0)
        logger.info("当前公网ip：%s", ip)
    except:
        logger.exception('解析ip失败！')
    return ip


def check_network():
    try:
        with request.urlopen('http://www.baidu.com', timeout=10) as res:
            if res.status == 200:
                logger.info('当前网络畅通！')
        return True
    except:
        logger.exception('请检查网络连接！')
    return False


def load_config(path):
    with open(path, 'r') as f:
        config = yaml.load(f.read(), yaml.FullLoader)
        if not config:
            raise ValueError('yaml文件不能为空！')
        if not isinstance(config, dict):
            raise ValueError('yaml文件格式有误！')

    return config