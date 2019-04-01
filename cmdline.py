import sys
import argparse


def cmd():
    parser = argparse.ArgumentParser(description=__doc__,
                                     epilog='GitHub:https://github.com/jianganfu/DDNSServer',
                                     add_help=False)
    parser.add_argument('-i', '--id', metavar='', help='AccessKey ID')
    parser.add_argument('-s', '--secret', metavar='', help='AccessKey Secret')
    parser.add_argument('-d', '--domain', metavar='', help='需要绑定的域名')
    parser.add_argument('-t', '--interval', metavar='', type=int, help='DNS更新时间 (default:%(default)s)', default=10)
    parser.add_argument('-h ', '--help', action='help', help='帮助命令')
    return parser.parse_args(sys.argv[1:])

