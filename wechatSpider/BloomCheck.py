#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pybloom_live import BloomFilter
import os
import hashlib


class BloomCheckFunction(object):
    def __init__(self):
        self.filename = 'bloomFilter.blm'
        is_exist = os.path.exists(self.filename)
        if is_exist:
            self.bf = BloomFilter.fromfile(open(self.filename, 'rb'))

        else:
            self.bf = BloomFilter(100000000, 0.001)

    def process_item(self, data):
        data_encode_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
        if data_encode_md5 in self.bf:
            # 内容没有更新 丢弃item
            self.save_bloom_file()
            return False

        else:
            self.bf.add(data_encode_md5)
            self.save_bloom_file()
            return True

    def save_bloom_file(self):
        self.bf.tofile(open(self.filename, 'wb'))
