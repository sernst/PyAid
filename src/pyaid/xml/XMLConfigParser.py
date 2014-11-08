# XMLConfigParser.py
# (C)2011
# Scott Ernst

from __future__ import print_function, absolute_import, unicode_literals, division

import re
import xml.dom.minidom as minidom
import codecs
from pyaid.dict.DictUtils import DictUtils
from pyaid.xml.ConfigData import ConfigData

#___________________________________________________________________________________________________ XMLConfigParser
class XMLConfigParser(object):
    """XMLConfigParser."""

#===================================================================================================
#                                                                                       C L A S S

    TYPE_ID = 'xml'

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ parseFile
    @staticmethod
    def parseFile(path, target=None, parseToInterchangeFormat =False):
        fh          = codecs.open(path, 'r', 'utf-8')
        xml         = fh.read()
        fh.close()
        return XMLConfigParser.parse(xml, target, parseToInterchangeFormat)

#___________________________________________________________________________________________________ parse
    @staticmethod
    def parse(xml, target=None, parseToInterchangeFormat =False):
        # Removes whitespace between tags to reduce potential parsing issues.
        pattern = re.compile('\<\?xml(.*)\?\>')
        if pattern.search(xml) is None:
            xml = '<?xml version="1.0" encoding="utf-8"?>' + xml
        dom = minidom.parseString(re.sub('>[\n\r\s\t]+<','><',xml))

        if target is None:
            target = {}

        cd = ConfigData()

        for node in dom.childNodes[0].childNodes:
            # Ignore whitespace generated text nodes
            if isinstance(node, (minidom.Comment, minidom.Text)):
                continue

            XMLConfigParser._parseNode(node, cd)

        if parseToInterchangeFormat:
            cd.writeToInterchangeDict(target)
        else:
            cd.writeToDict(target)

        return target

#___________________________________________________________________________________________________ serializeToFile
    @staticmethod
    def serializeToFile(targetFile, interchangeData):
        xml = XMLConfigParser.serializeToXML(interchangeData)
        fh  = codecs.open(targetFile, 'wb', 'utf-8')
        fh.write(xml)
        fh.close()

#___________________________________________________________________________________________________ serialize
    @staticmethod
    def serialize(interchangeData):
        xml = '<vm>\n'
        for n,v in DictUtils.iter(interchangeData):
            xml += XMLConfigParser._writeNode(n, v)
        return (xml + '</vm>').decode('unicode_escape')

#===================================================================================================
#                                                                                  P R I V A T E

#___________________________________________________________________________________________________ _writeNode
    @staticmethod
    def _writeNode(name, data, depth =1):
        indent = (' '*4*depth)
        target = indent + '<'
        if isinstance(data, list):
            d = '|'.join(data[1]) if isinstance(data[1], list) else str(data)
            target += data[0] + ' n="' + name + '" v="' + d + '" />\n'
        elif isinstance(data, dict):
            target += 'o n="' + name + '">\n'
            for n,v in DictUtils.iter(data):
                target += XMLConfigParser._writeNode(n, v, depth+1)
            target += indent + '</o>'
        elif isinstance(data, str):
            target += 's' + 'n="' + name + '" v="' + data + '" />\n'
        elif isinstance(data, (int, float)):
            target += 'n' + 'n="' + name + '" v="' + str(data) + '" />\n'
        else:
            target += 'unknown n="' + name + '" />'

        return target

#___________________________________________________________________________________________________ _parseNode
    @staticmethod
    def _parseNode(node, configData):
        nodeName = node.getAttribute('n')
        nodeType = node.tagName

        if nodeType != 'o':
            XMLConfigParser._parseAttribute(nodeName, nodeType, node.getAttribute('v'), configData)
            return

        cd = ConfigData()
        for k in node.attributes.keys():
            if k != 'n':
                aValue = node.getAttribute(k)
                aType  = 's'
                if aValue.find(':') != -1:
                    aValue = node.getAttribute(k).split(':')
                    aType  = str(aValue[0])
                    aValue = aValue[-1]
                XMLConfigParser._parseAttribute(k, aType, aValue, cd)

        for child in node.childNodes:
            XMLConfigParser._parseNode(child, cd)

        configData.setItem(nodeName, 'o', cd)

#___________________________________________________________________________________________________ _parseAttribute
    @staticmethod
    def _parseAttribute(attrName, attrType, attrValue, configData):
        configData.setItem(attrName, attrType, attrValue)
