import os
import time
import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException

from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest

from utils import get_ip, check_network, logger, load_config
from cmdline import cmd


class DDNS(object):
    def __init__(self, access_key_id, access_key_secret, domain):
        # 将阿里云获取的AccessKeyId和AccessKeySecret作为验证的凭据
        self.client = AcsClient(access_key_id, access_key_secret, max_retry_time=3,
                                timeout=10)
        # 需要绑定的域名
        self.domain = domain
        self.is_update = True

    def add_record(self, ip):
        """
        通过api增加DNS解析记录
        :param ip: 需要绑定的ip
        :return: None
        """
        adr = AddDomainRecordRequest()
        adr.set_DomainName(self.domain)
        adr.set_RR('www')
        adr.set_Type('A')
        adr.set_Value(ip)
        try:
            response = self.client.do_action_with_exception(adr)
            res = json.loads(response.decode('utf-8'))
            logger.info('DNS记录[%s]创建成功！', res['RecordId'])
        except:
            logger.exception('DNS创建失败！')

    def record_update(self, record, ip):
        """
        通过api更新DNS
        :param record: 字典格式的解析记录
        :param ip: 需要绑定的ip值
        :return: None
        """
        udr = UpdateDomainRecordRequest()
        udr.set_RecordId(record['RecordId'])
        udr.set_RR(record['RR'])
        udr.set_Type(record['Type'])
        udr.set_Value(ip)
        try:
            response = self.client.do_action_with_exception(udr)
            res = json.loads(response.decode('utf-8'))
            logger.info('DNS记录[%s]重新绑定成功！', res['RecordId'])
        except:
            logger.exception('DNS重新绑定失败！')

    def update(self):
        """
        更新DNS解析
        :return: None
        """
        # 检测网络,如果网络不畅通,则取消操作
        res = check_network()
        if not res:
            return
        ip = self.save_ip_to_local()
        # 如果当前ip和上一次的ip一致，则不进行DNS绑定更新
        if not self.is_update:
            logger.info('公网[%s]暂未改变，无需重新绑定！', ip)
            return
        ddr = DescribeDomainRecordsRequest()
        ddr.set_DomainName(self.domain)
        try:
            response = self.client.do_action_with_exception(ddr)
            records = json.loads(response.decode('utf-8'))
            # 如果此时域名未进行任何绑定,自动增加绑定记录
            if not records['DomainRecords']['Record']:
                self.add_record(ip)
            # 对数据进行解析
            for record in records['DomainRecords']['Record']:
                # 只对www.XXX.com或者XXX.com的记录生效
                if record['RR'] not in ['www', '@']:
                    continue
                if record['Value'] != ip:
                    self.record_update(record, ip)

        except ServerException:
            logger.exception('阿里云DNS解析失败！')

    def save_ip_to_local(self):
        """
        利用爬虫获取本地的IP，并将IP保存到文件中，作为缓存
        :return: 返回本地公网ip
        """
        new_ip = get_ip()
        if new_ip:
            if not os.path.exists('ip.cache'):
                with open('ip.cache', 'w'):
                    pass
            with open('ip.cache', 'r+') as f:
                old_ip = f.read()
                f.seek(0)
                # 比较当前IP是否和上一次的IP是否相同，如果相同,则不写入缓存文件，同时也不进行DNS更新
                if old_ip != new_ip:
                    # 清空文件
                    f.truncate()
                    f.write(new_ip)
                    self.is_update = True
                else:
                    self.is_update = False
        return new_ip


def run():
    # 命令行参数优先级更高
    config = vars(cmd())
    if (not config.get('id')) or (not config.get('secret')) or (not config.get('domain')):
        try:
            temp = load_config('config.yaml')
            config.update(temp)
        except FileNotFoundError as e:
            logger.error('配置文件不存在！')
            raise e
        except ValueError as e:
            logger.error('配置文件格式错误！')
            raise e
    ak_id = config['id']
    ak_st = config['secret']
    domain = config['domain']
    # DNS更新时间默认10分钟
    update_interval = config.get('interval')

    ddns = DDNS(ak_id, ak_st, domain)

    while True:
        ddns.update()
        # 指定重新更改ip的间隔
        time.sleep(update_interval * 60)


if __name__ == "__main__":
    run()
