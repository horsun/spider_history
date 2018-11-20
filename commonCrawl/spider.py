import time
from pprint import pprint

import requests
from lxml import html as lxml_html
import re
import json
import bs4


class CommonCrawler():
    def __init__(self):

        pass

    def format_function(self, format_string):
        """
        here to process format with your formate rules
        """
        if format_string == 'list_to_string':
            def formatter_fuc(target_list):
                better_data = ''
                for item in target_list:
                    better_data += item
                data = [better_data]
                return data
        elif format_string == '%Y-%m-%d %H:%M:%S':
            def formatter_fuc(stamp):
                if isinstance(stamp, list):
                    return_data = []
                    for stam in stamp:
                        value = None
                        if len(str(int(stam))) == 10:
                            value = stamp
                        if len(str(int(stam))) == 13:
                            value = stam / 1000
                        if len(str(int(stam))) == 7:
                            value = stam * 1000
                        return_data.append(time.strftime(format_string, time.localtime(int(value))))
                    return return_data
                else:
                    value = None
                    if len(str(int(stamp))) == 10:
                        value = stamp
                    if len(str(int(stamp))) == 13:
                        value = stamp / 1000
                    if len(str(int(stamp))) == 7:
                        value = stamp * 1000
                    return time.strftime(format_string, time.localtime(int(value)))

        return formatter_fuc

    def json_to_string(self, data):
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False).strip()

    def startRequest(self, url):
        html = requests.get(url=url).text
        host = url.split('/')[2]
        return self.runParseRule(host, html)

    def transform_list_and_dict(self, list_or_dict):
        # TODO 这里进行转换 list to dict
        final_data = []
        for key in list_or_dict:
            for num, value in enumerate(list_or_dict[key]):
                if final_data.__len__() < list_or_dict[key].__len__():
                    final_data.append({
                        key: value
                    })
                elif final_data.__len__() == list_or_dict[key].__len__():
                    final_data[num][key] = value
        return final_data

    def getParseRule(self, host, path=None, query=None):
        """
        here to add your \web host \ data type\rules 
        """
        rule_mix = {
            # https://campus.jd.com/web/job/job_list
            'campus.jd.com': [{
                'dataType': 'json.list',
                'ruleType': 'jsonPath',
                'urlPath': '/web/job/job_list',
                'rules': {
                    'jobName': ('jobList[].jobName', None),
                    'jobCategoryName': ('jobList[].jobCategoryName', None),
                    'description': ('jobList[].description', None),
                    'jobDirection': ('jobList[].jobDirection', None),
                    'companyName': ('jobList[].jobCompanyList[*].companyName', None),
                    'interviewPlaceName': ('jobList[].interviewPlaceName', None),
                    'itemJson': ('jobList[].*', None),
                    'createTime': ('jobList[].createTime', self.format_function("%Y-%m-%d %H:%M:%S")),
                    'modifyTime': ('jobList[].modifyTime', self.format_function("%Y-%m-%d %H:%M:%S"))
                }
            }],
            # https://app.yingjiesheng.com/app/?module=famousview&sessid=&userid=&cid=496
            'app.yingjiesheng.com': [{
                'urlPath': '/app',
                'dataType': 'json.list',
                'ruleType': 'jsonPath',
                'rules': {
                    'jobName': ('resultbody.items[].content', None),
                    'addtime': ('resultbody.items[].addtime', self.format_function("%Y-%m-%d %H:%M:%S")),
                }
            }],
            # https://bbsapp.yingjiesheng.com/51jobyjs.php?act=get_view_thread&tid=2155899
            'bbsapp.yingjiesheng.com': [{
                'urlPath': '/51jobyjs.php',
                'dataType': 'json.detail',
                'ruleType': 'jsonPath',
                'rules': {
                    'title': ('title', None),
                    'from': ('from', None),
                }
            }],
            'jobs.zhaopin.com': [{
                # host: 'xx.xx.com', path: '/path1', query: 'method=action1'
                # method => http://xx.xx.com/path1?method=action1
                'dataType': 'Xpath_detail',
                'ruleType': 'htmlXpath',
                'urlPath': '/path1',
                'urlQuery': 'method=action1',
                'rules': {
                    "jobName": ('//div[5]/div[1]/div[1]/h1/text()', None),
                    "jobDesc": ('//div[6]/div[1]/div[1]/div/div[1]/p/text()', self.format_function('list_to_string')),
                    "companyName": ('//div[5]/div[1]/div[1]/h2/a/text()', None),
                    "jobMonthMoney": ('//div[6]/div[1]/ul/li[1]/strong/text()', None),
                    "jobAddress": ('//div[6]/div[1]/ul/li[2]/strong/a/text()', None),
                    "experienceNeed": ('//div[6]/div[1]/ul/li[5]/strong/text()', None),
                }
            }, {
                # host: 'xx.xx.com', path: '/path1', query: 'method=action2'
                # method => http://xx.xx.com/path1?method=action2
                'urlPath': '/path1',
                'urlQuery': 'method=action2'
            }]
        }
        rule_list = rule_mix[host]
        for rule in rule_list:
            if path is not None or query is not None:
                if rule['urlPath'] == path or rule['urlQuery'] == query:
                    pass
            else:
                return rule_list[0]
        # TODO: Find best match rule #

    def runParseRule(self, host, html):
        """
        here to process crawl with your setted rules
        """
        host_rules = self.getParseRule(host)
        rules = host_rules['rules']
        example_data = {}
        if host_rules['dataType'] in ['json.list', 'json.detail']:
            main_data = json.loads(html)
            for rule_name in rules:
                rule, formatter = rules[rule_name]
                data = []
                # 有[] 和 [*]的参照addr list
                old_addr_list = rule.split('.')
                # 没有 []  和 [*] 的参照 addr list
                addr_list = [item.split('[')[0] for item in rule.split('.')]
                # 需要取出list
                list_index = None
                string_index = None
                item_list = None
                all_info_index = None
                if '[].*' not in rule:
                    json_data = main_data
                    if '[]' in rule:
                        # 取出 [] 所在的位置
                        list_index = old_addr_list.index([x for x in old_addr_list if '[]' in x][0])
                    if '[*]' in rule:
                        # [*] 的位置
                        string_index = old_addr_list.index([x for x in old_addr_list if '[*]' in x][0])
                    string_list = []
                    for num, addr in enumerate(addr_list):
                        # string_index 肯定比 list_index 大
                        # 如果 位置没到 list_index 就循环到 到list_index
                        # 如果 位置到了 list_index item_list 就是列表 其中进行 data的内容的扩充
                        # 如果 循环继续 到了string_index item_list 就是 当到了num>string index 就取string
                        if list_index != None:
                            # TODO 这里进行多页内容获取
                            if string_index != None and (num >= string_index):
                                if num == string_index:
                                    for top_item in item_list:
                                        string_list.append(top_item[addr])
                                elif num > string_index:
                                    data.clear()
                                    for low_item_list in string_list:
                                        item_string = ''
                                        for low_item in low_item_list:
                                            item_string += low_item[addr].strip() + ','
                                        data.append(item_string)
                            elif num == list_index:
                                item_list = json_data[addr]
                            elif num > list_index and num != string_index:
                                for item in item_list:
                                    data.append(item[addr])
                            elif num < list_index:
                                json_data = json_data[addr]
                        elif list_index == None:
                            # TODO 这里进行单页内容获取
                            if string_index != None and (num >= string_index):
                                if num == string_index:
                                    for top_item in item_list:
                                        string_list.append(top_item[addr])
                                elif num > string_index:
                                    data.clear()
                                    for low_item_list in string_list:
                                        item_string = ''
                                        for low_item in low_item_list:
                                            item_string += low_item[addr].strip() + ','
                                        data.append(item_string)
                            elif addr_list.__len__() == 1:

                                data.append(json_data[addr])

                            elif num < addr_list.__len__():
                                json_data = json_data[addr]
                else:
                    # TODO 这里进行单个detail获取
                    json_data = main_data
                    all_info_index = old_addr_list.index([x for x in old_addr_list if '*' in x][0])
                    for num, addr in enumerate(addr_list):
                        if num == all_info_index:
                            for item in json_data:
                                data.append(self.json_to_string(item))
                        elif num < all_info_index:
                            json_data = json_data[addr]
                if formatter is not None:
                    data = formatter(data)
                example_data[rule_name] = data

            return self.transform_list_and_dict(example_data)
        elif host_rules['ruleType'] == 'htmlXpath':
            doc = lxml_html.fromstring(html)
            example_data = {}
            for rule_name in rules:
                rule, formatter = rules[rule_name]
                data = None
                if host_rules['dataType'] == 'Xpath_detail':
                    data = [item.strip() for item in doc.xpath(rule)]
                    if formatter is not None:
                        data = formatter(data)
                    example_data[rule_name] = data
                if host_rules['dataType'] == 'Xpath_list':
                    data = doc.xpath(rule)
                    if formatter is not None:
                        data = formatter(doc.xpath(rule))
                    example_data[rule_name] = data
            return self.transform_list_and_dict(example_data)
        # elif
        # TODO: deal with other dataType


if __name__ == '__main__':
    # https://app.yingjiesheng.com/app/?module=famousview&sessid=&userid=&cid=496
    # https://campus.jd.com/web/job/job_list
    # https://bbsapp.yingjiesheng.com/51jobyjs.php?act=get_view_thread&tid=2155899
    # https://jobs.zhaopin.com/CC000212281J00146109005.htm #xpath

    c = CommonCrawler()
    url = 'https://campus.jd.com/web/job/job_list'
    result = c.startRequest(url)
    pprint(result)
