# MakoRenderer.py
# (C)2012-2013
# Scott Ernst

from mako.lookup import TemplateLookup
from mako import exceptions

from pyaid.debug.Logger import Logger
from pyaid.web.DomUtils import DomUtils
from pyaid.web.mako.MakoDataTransporter import MakoDataTransporter

#___________________________________________________________________________________________________ MakoRenderer
class MakoRenderer(object):
    """A class for..."""

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, template, rootPath, data =None, logger =None, minify =False):
        """Creates a new instance of ClassTemplate."""
        self._template = template
        self._data     = data if data else {}
        self._error    = None
        self._minify   = minify
        self._errorMsg = ''
        self._rootDir  = rootPath
        self._result   = None
        self._log      = logger if logger else Logger(self)

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: data
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, value):
        self._data = value

#___________________________________________________________________________________________________ GS: template
    @property
    def template(self):
        return self._template
    @template.setter
    def template(self, value):
        self._template = value

#___________________________________________________________________________________________________ GS: success
    @property
    def success(self):
        return self._result is not None and self._error is None

#___________________________________________________________________________________________________ GS: error
    @property
    def error(self):
        return self._error

#___________________________________________________________________________________________________ GS: errorMessage
    @property
    def errorMessage(self):
        return self._errorMsg

#___________________________________________________________________________________________________ GS: dom
    @property
    def dom(self):
        return self._result if self._result else u''

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ render
    def render(self, **kwargs):
        """Doc..."""

        # ADD KWARGS TO TEMPLATE RENDER PROPERTIES
        if kwargs:
            data = dict(self._data.items() + kwargs.items())
        else:
            data = self._data

        td = [self._rootDir]

        lookup = TemplateLookup(
            directories=td,
            input_encoding='utf-8',
            output_encoding='utf-8',
            encoding_errors='replace'
        )

        template = self._template
        if not template.startswith('/'):
            template = '/' + template

        try:
            target = lookup.get_template(template)
        except Exception, err:
            self._result   = None
            self._error    = err
            self._errorMsg = 'Failed to get template (%s):\n%s' % (
                template,
                exceptions.text_error_template().render().replace('%','%%')
            )
            self._log.writeError(self._errorMsg, self._error)
            return self.dom

        mr = MakoDataTransporter(data=data, logger=self._log)
        try:
            self._result = target.render_unicode(mr=mr)
        except Exception, err:
            d = []
            if data:
                for n,v in data.iteritems():
                    d.append(str(n) + ': ' + str(v))

            try:
                stack = exceptions.text_error_template().render().replace('%','%%')
            except Exception, err2:
                stack = ''
                self._log.writeError('Unable to build mako exception stack', err2)

            traces = mr.getTraces()
            self._errorMsg = 'Failed to render (%s):\n%s\n%sDATA:\n\t%s' % (
                str(template),
                str(stack),
                ('TRACES:\n\t' + '\n\t'.join(traces) if traces else ''),
                '\n\t'.join(d) if d else ''
            )
            self._log.write(self._errorMsg)

        if self._minify:
            return self.minifyResult()

        return self.dom

#___________________________________________________________________________________________________ minifyResult
    def minifyResult(self):
        if not self._result:
            return self._result

        self._result = DomUtils.minifyDom(self._result)
        return self._result
