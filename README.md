# 使用Python3 + 阿里云DNS解析实现DDNS

## 1、准备

- 公网ip
- 阿里云域名
- python3环境

## 2、执行

- 下载依赖包(**requirements.txt中的是环境Python3.6.5,其他版本需自己下载依赖库**)

  ```
  pip install aliyun-python-sdk-core-v3
  pip install aliyun-python-sdk-alidns
  pip install chardet
  pip install pyyaml
  ```

  

- 终端执行

  进入主目录

  ```bash
  python server.py [options] 
  ```

  |   可选参数    |              功能               | 可选 |
  | :-----------: | :-----------------------------: | :--: |
  |   -h,--help   |          调出帮助文档           |  是  |
  |    -i,--id    |        指定AccessKey ID         |  是  |
  |  -s,--secret  |        指定AccessKey Secret         |  是  |
  |  -d,--domain  | 指定需要绑定的域名(不用包含www) |  是  |
  | -t,--interval |   指定DNS更新时间(默认10分钟)   |  是  |

  **注意:** 当`id`,`sercret`,`domain`在命令行未指定时,必须手动创建`config.yaml`文件(主目录下),主要内容如下:

  ```yaml
  id: 你的AccessKey ID
  secret: 你的AccessKey Secret
  domain: 你的域名(不用包含www)
  interval: 10
  # 由于interval已经有默认值，可以不用指定
  ```

  **命令行给定的参数优先级大于`config.yaml`中的参数**

## 3、更改路由器映射

需要手动更改路由器的映射规则,查看https://jingyan.baidu.com/article/647f0115fc82447f2148a8ed.html

