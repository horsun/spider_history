#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging

logger = logging.getLogger('xj.common.config')

import os
import json

__CONFIG_DIR__ = '.config'
__CONFIG_JSON__ = '.json'
__CONFIG_PROPERTIES__ = '.properties'


class Struct:
    def __init__(self, entries, configName):
        self.configName = configName
        self.jsonObj = entries
        for key in entries:
            value = entries[key]
            if isinstance(value, dict):
                self.__dict__[key] = Struct(value, u'%s.%s' % (self.configName, key))
            else:
                self.__dict__[key] = value

    def json(self):
        return self.jsonObj

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name.startswith('has'):
            propertieName = name.split('has')[-1]
            if propertieName in self.__dict__:
                return True
            return False
        else:
            raise Exception(u'Cannot found "%s" in "%s"' % (name, self.configName))


class ConfigHelper(object):
    def __init__(self):
        currentDir = os.path.dirname(os.path.abspath(__file__))
        while __CONFIG_DIR__ not in os.listdir(currentDir):
            tmpDir = os.path.abspath(os.path.join(currentDir, u'..'))
            if tmpDir == currentDir:
                break
            currentDir = tmpDir
        configDir = os.path.join(currentDir, __CONFIG_DIR__)
        for fileName in os.listdir(configDir):
            fullPath = os.path.join(configDir, fileName)
            if os.path.isfile(fullPath):
                shortName, ext = os.path.splitext(fileName)
                if ext == __CONFIG_JSON__:
                    self.__readJson__(shortName, fullPath)
                elif ext == __CONFIG_PROPERTIES__:
                    self.__readProperties__(shortName, fullPath)

    def __readJson__(self, configName, filePath):
        logger.debug(u'readJson() | Name: %s, Path: %s' % (configName, filePath))
        with open(filePath) as fp:
            setattr(self, configName, Struct(json.load(fp), configName))

    def __valueTrans__(self, value):
        if value == 'True' or value == 'true':
            return True
        if value == 'False' or value == 'false':
            return False
        try:
            if int(value) == float(value):
                return int(value)
            return float(value)
        except Exception as e:
            try:
                return float(value)
            except Exception as e:
                return value

    def __readProperties__(self, configName, filePath):
        logger.debug(u'readProperties() | Name: %s, Path: %s' % (configName, filePath))
        configMap = {}
        with open(filePath, 'r', encoding='utf-8') as fp:
            for line in fp:
                try:
                    line = line
                except Exception as e:
                    pass
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith('#'):
                    continue
                tmpArr = line.split('=')
                if len(tmpArr) < 2:
                    logger.warn(u'readProperties() | Read config "%s" fail' % (line))
                    continue
                left = tmpArr[0].strip()
                right = u'='.join(tmpArr[1:]).strip()
                if u'.' not in left:
                    configMap[left] = self.__valueTrans__(right)
                else:
                    currentMap = configMap
                    keyList = left.split('.')
                    while len(keyList) > 0:
                        key = keyList[0]
                        if len(keyList) == 1:
                            currentMap[key] = self.__valueTrans__(right)
                        else:
                            if key not in currentMap:
                                tmpMap = {}
                                currentMap[key] = tmpMap
                                currentMap = tmpMap
                            else:
                                currentMap = currentMap[key]
                        del keyList[0]
        setattr(self, configName, Struct(configMap, configName))

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name.startswith('has'):
            configName = name.split('has')[-1]
            if configName in self.__dict__:
                return True
            return False
        return None


Config = ConfigHelper()

if __name__ == "__main__":
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(threadName)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.debug(Config.test.Hello)
    logger.debug(Config.test.World)
    logger.debug(Config.test.Python.json())
    logger.debug(Config.test.Python.Key1)
    logger.debug(Config.test.Python.Sub.Key1)

    logger.debug(Config.Test.Hello)
    logger.debug(Config.Test.World)
    logger.debug(Config.Test.Python.json())
    logger.debug(Config.Test.Python.Key1)
    logger.debug(Config.Test.Python.Sub.Key1)

    logger.debug(Config.test.hasPython)
    logger.debug(Config.test.hasPython2)
    logger.debug(Config.test.Python.KeyNotExist)
