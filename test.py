import yaml
try:
    with open('configa.yaml', 'r') as f:
        config = yaml.load(f.read(), yaml.FullLoader)
        if not isinstance(config, dict):
            print("请填写正确的yaml格式！")
            raise ValueError('yaml文件格式有误！')
    print(config, type(config))
except Exception as e:
    print('yaml文件不存在！')
    raise e

