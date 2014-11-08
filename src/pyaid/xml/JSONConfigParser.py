# JSONConfigParser.py
# (C)2011
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import json
import codecs
from pyaid.dict.DictUtils import DictUtils
from pyaid.xml.ConfigData import ConfigData

#___________________________________________________________________________________________________ JSONConfigParser
class JSONConfigParser(object):
    """JSONConfigParser."""

#===================================================================================================
#                                                                                       C L A S S

    TYPE_ID = 'json'

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ parseFile
    @staticmethod
    def parseFile(path, target=None, parseToInterchangeFormat =False):
        fh   = codecs.open(path, 'r', 'utf-8')
        data = fh.read()
        fh.close()
        return JSONConfigParser.parse(data, target, parseToInterchangeFormat)

#___________________________________________________________________________________________________ parse
    @staticmethod
    def parse(data, target=None, parseToInterchangeFormat =False):
        d = json.loads(data)

        if target is None:
            target = {}

        cd = ConfigData()

        for n,v in DictUtils.iter(d):
            JSONConfigParser._parseElement(n, v, cd)

        if parseToInterchangeFormat:
            cd.writeToInterchangeDict(target)
        else:
            cd.writeToDict(target)

        return target

#___________________________________________________________________________________________________ serializeToFile
    @staticmethod
    def serializeToFile(targetFile, interchangeData):
        data = JSONConfigParser.serializeToJSON(interchangeData)
        fh   = codecs.open(targetFile, 'wb', 'utf-8')
        fh.write(data)
        fh.close()

#___________________________________________________________________________________________________ serialize
    @staticmethod
    def serialize(interchangeData):
        data = {}
        for n,v in DictUtils.iter(interchangeData):
            data[n] = JSONConfigParser._createElement(v)
        return json.dumps(data, separators=(',', ':')).decode('unicode_escape')

#===================================================================================================
#                                                                                  P R I V A T E

#___________________________________________________________________________________________________ _createElement
    @staticmethod
    def _createElement(data):
        if isinstance(data, list):
            if isinstance(data[1], list):
                out = []
                for v in data[1]:
                    out.append(str(v))
                d = '|'.join(out)
            else:
                d = data[1]

            return [data[0], d]
        elif isinstance(data, dict):
            d = {}
            for n,v in DictUtils.iter(data):
                d[n] = JSONConfigParser._createElement(v)
            return d

        return data

#___________________________________________________________________________________________________ _parseElement
    @staticmethod
    def _parseElement(name, value, configData):
        if isinstance(value, list):
            configData.setItem(name, value[0], value[1])
        elif isinstance(value, str):
            configData.setItem(name, 's', value)
        elif isinstance(value, (int, float)):
            configData.setItem(name, 'n', value)
        elif isinstance(value, dict):
            cd = ConfigData()
            for n,v in DictUtils.iter(value):
                JSONConfigParser._parseElement(n, v, cd)
            configData.setItem(name, 'o', cd)
