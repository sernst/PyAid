# ColorValue.py
# (C)2011-2013
# Scott Ernst

import re
import math
import numbers

#___________________________________________________________________________________________________ ColorValue
from pyaid.color.ColorNames import ColorNames
from pyaid.string.StringUtils import StringUtils


class ColorValue(object):
    """A class for working with colors in various color spaces."""

    _BEND_FINDER        = re.compile('[+-]+$')
    _HEX_COLOR_PATTERN  = re.compile('[^A-Fa-f0-9]+')

#===================================================================================================
#                                                                                       C L A S S

#___________________________________________________________________________________________________ __init__
    def __init__(self, sourceColor, normalized =False, opacity =1.0):
        """Creates a new instance of ColorValue."""

        self._rawColor = 0
        self._opacity  = opacity
        self._setColor(sourceColor, normalized)

        # Cached color formats
        self._hslColor              = None
        self._hslNormColor          = None
        self._rgbColor              = None
        self._rgbNormColor          = None
        self._hsvColor              = None
        self._hsvNormColor          = None
        self._webColor              = None
        self._webCompactColor       = None
        self._lumaColor             = None
        self._shiftUpColors         = None
        self._shiftDownColors       = None

#===================================================================================================
#                                                                                   G E T / S E T

#___________________________________________________________________________________________________ GS: intRgb
    @property
    def intRgb(self):
        return self._rawColor
    @intRgb.setter
    def intRgb(self, value):
        self._rawColor = int(value)
        self._unCache()

#___________________________________________________________________________________________________ GS: intAlpha
    @property
    def intAlpha(self):
        return int(round(255.0*self._opacity))
    @intAlpha.setter
    def intAlpha(self, value):
        self._opacity  = float(int(value))/255.0
        self._unCache()

#___________________________________________________________________________________________________ GS: intRgba
    @property
    def intRgba(self):
        return (self._rawColor << 8) & self.intAlpha
    @intRgba.setter
    def intRgba(self, value):
        value          = int(value)
        self._opacity  = float(value & 0xFF)/255.0
        self._rawColor = value >> 8
        self._unCache()

#___________________________________________________________________________________________________ GS: opacity
    @property
    def opacity(self):
        return self._opacity
    @opacity.setter
    def opacity(self, value):
        self._opacity = float(value)

#___________________________________________________________________________________________________ GS: hexRgb
    @property
    def hexRgb(self):
        return hex(self._rawColor)
    @hexRgb.setter
    def hexRgb(self, value):
        self.intRgb = int(value, 8)

#___________________________________________________________________________________________________ GS: hexRgba
    @property
    def hexRgba(self):
        return hex(self.intRgba)
    @hexRgba.setter
    def hexRgba(self, value):
        self.intRgba = int(value, 8)

#___________________________________________________________________________________________________ GS: hexAlpha
    @property
    def hexAlpha(self):
        return hex(self.intAlpha)
    @hexAlpha.setter
    def hexAlpha(self, value):
        self.intAlpha = int(value, 8)
        self._unCache()

#___________________________________________________________________________________________________ GS: bareHex
    @property
    def bareHex(self):
        return self._getWebValue(False).replace('#','')

#___________________________________________________________________________________________________ GS: webRgbOpacity
    @property
    def webRgbOpacity(self):
        return self.asWebRgbOpacity()

#___________________________________________________________________________________________________ GS: webRGBA
    @property
    def webRGBA(self):
        return self.asWebRGBA()

#___________________________________________________________________________________________________ GS: web
    @property
    def web(self):
        return self._getWebValue(False)
    @web.setter
    def web(self, value):
        self._setColor(value)

#___________________________________________________________________________________________________ GS: webCompact
    @property
    def webCompact(self):
        return self._getWebValue(True)
    @webCompact.setter
    def webCompact(self, value):
        self._setColor(value)

#___________________________________________________________________________________________________ GS: red
    @property
    def red(self):
        return self._getRGBValue(0, False)
    @red.setter
    def red(self, value):
        rgb = self.asRgb()
        rgb['r'] = value
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: green
    @property
    def green(self):
        return self._getRGBValue(1, False)
    @green.setter
    def green(self, value):
        rgb = self.asRgb()
        rgb['g'] = value
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: blue
    @property
    def blue(self):
        return self._getRGBValue(2, False)
    @blue.setter
    def blue(self, value):
        rgb = self.asRgb()
        rgb['b'] = value
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: redNorm
    @property
    def redNorm(self):
        return self._getRGBValue(0, True)
    @redNorm.setter
    def redNorm(self, value):
        rgb = self.asRgb()
        rgb['r'] = round(255*value)
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: greenNorm
    @property
    def greenNorm(self):
        return self._getRGBValue(1, True)
    @greenNorm.setter
    def greenNorm(self, value):
        rgb = self.asRgb()
        rgb['g'] = round(255*value)
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: blueNorm
    @property
    def blueNorm(self):
        return self._getRGBValue(2, True)
    @blueNorm.setter
    def blueNorm(self, value):
        rgb = self.asRgb()
        rgb['b'] = round(255*value)
        self._setColor(rgb)

#___________________________________________________________________________________________________ GS: hue
    @property
    def hue(self):
        return self._getHSVValue(0, False)
    @hue.setter
    def hue(self, value):
        hsv = self.asHsv()
        hsv['h'] = value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: saturation
    @property
    def saturation(self):
        return self._getHSVValue(1, False)
    @saturation.setter
    def saturation(self, value):
        hsv = self.asHsv()
        hsv['s'] = value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: brightness
    @property
    def brightness(self):
        return self._getHSVValue(2, False)
    @brightness.setter
    def brightness(self, value):
        hsv = self.asHsv()
        hsv['v'] = value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: hueNorm
    @property
    def hueNorm(self):
        return self._getHSVValue(0, True)
    @hueNorm.setter
    def hueNorm(self, value):
        hsv = self.asHsv()
        hsv['h'] = 360.0*value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: saturationNorm
    @property
    def saturationNorm(self):
        return self._getHSVValue(1, True)
    @saturationNorm.setter
    def saturationNorm(self, value):
        hsv = self.asHsv()
        hsv['s'] = 0.01*value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: brightnessNorm
    @property
    def brightnessNorm(self):
        return self._getHSVValue(2, True)
    @brightnessNorm.setter
    def brightnessNorm(self, value):
        hsv = self.asHsv()
        hsv['v'] = 0.01*value
        self._setColor(hsv)

#___________________________________________________________________________________________________ GS: hslHue
    @property
    def hslHue(self):
        return self._getHSLValue(0, False)
    @hslHue.setter
    def hslHue(self, value):
        hsl = self.asHsl()
        hsl['h'] = value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: hslSaturation
    @property
    def hslSaturation(self):
        return self._getHSLValue(1, False)
    @hslSaturation.setter
    def hslSaturation(self, value):
        hsl = self.asHsl()
        hsl['s'] = value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: lightness
    @property
    def lightness(self):
        return self._getHSLValue(2, False)
    @lightness.setter
    def lightness(self, value):
        hsl = self.asHsl()
        hsl['l'] = value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: hslHueNorm
    @property
    def hslHueNorm(self):
        return self._getHSLValue(0, True)
    @hslHueNorm.setter
    def hslHueNorm(self, value):
        hsl = self.asHsl()
        hsl['h'] = 360.0*value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: hslSaturationNorm
    @property
    def hslSaturationNorm(self):
        return self._getHSLValue(1, True)
    @hslSaturationNorm.setter
    def hslSaturationNorm(self, value):
        hsl = self.asHsl()
        hsl['s'] = 0.01*value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: lightnessNorm
    @property
    def lightnessNorm(self):
        return self._getHSLValue(2, True)
    @lightnessNorm.setter
    def lightnessNorm(self, value):
        hsl = self.asHsl()
        hsl['l'] = 0.01*value
        self._setColor(hsl)

#___________________________________________________________________________________________________ GS: luma
    @property
    def luma(self):
        return self.asLuma()

#___________________________________________________________________________________________________ GS: shiftColors
    @property
    def shiftColors(self):
        if self.brightness < 60.0:
            return self.shiftUpColors

        return self.shiftDownColors

#___________________________________________________________________________________________________ GS: deeperColors
    @property
    def deeperColors(self):
        if self.brightness > 10.0:
            return self.shiftDownColors

        return self.shiftUpColors

#___________________________________________________________________________________________________ GS: shiftUpColors
    @property
    def shiftUpColors(self):
        if self._shiftUpColors:
            return self._shiftUpColors

        delta = min(math.floor((100 - self.brightness)/3.0), 10)
        res   = []
        for i in range(1, 5):
            c    = self.clone()
            c.hsvShift(v=i*delta)
            res.append(c)

        self._shiftUpColors = res
        return res

#___________________________________________________________________________________________________ GS: shiftDownColors
    @property
    def shiftDownColors(self):
        if self._shiftDownColors:
            return self._shiftDownColors

        delta = min(math.floor(self.brightness/3.0), 10)
        res   = []
        for i in range(1, 5):
            c    = self.clone()
            c.hsvShift(v=-i*delta)
            res.append(c)

        self._shiftDownColors = res
        return res

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ getColorNameAndValue
    def getColorNameAndValue(self):
        """ Finds the nearest named color by comparing all named colors """
        if self._rawColor == 0:
            return {
                'name':'Black',
                'value':0,
                'key':'black',
                'residual':0.0 }

        maxRange = 560.0
        nearestValue = None
        nearestName  = None
        range   = 360
        myColor = self.asHsl(output=list)
        poolColor = self.__class__(0)
        for name, value in ColorNames.NAMES.iteritems():
            poolColor.load(value)
            color = poolColor.asHsl(output=list)

            test = (myColor[0] - color[0])*(myColor[0] - color[0]) \
                + (myColor[1] - color[1])*(myColor[1] - color[1]) \
                + (myColor[2] - color[2])*(myColor[2] - color[2])
            if test < range:
                nearestValue = value
                nearestName  = name
                range        = test
            if range < 1:
                break

        return {
            'name':StringUtils.capitalizeWords(nearestName.replace('_', ' ')),
            'value':nearestValue,
            'key':nearestName,
            'residual':100.0*range/maxRange }

#___________________________________________________________________________________________________ toDict
    def toDict(self):
        return self.createDict(color=self._rawColor, alpha=self._opacity)

#___________________________________________________________________________________________________ createDict
    @classmethod
    def createDict(cls, color, alpha =1.0):
        return {'color':color, 'alpha':alpha}

#___________________________________________________________________________________________________ fromDict
    def fromDict(self, value):
        if 'alpha' in value:
            self._opacity = value.get('alpha', 1.0)
        elif 'opacity' in value:
            self._opacity = value.get('opacity', 1.0)
        else:
            self._opacity = 1.0

        v = value.get('color')
        if isinstance(v, (int, long)):
            self._rawColor = int(v)
        else:
            self.load(v)

#___________________________________________________________________________________________________ copyFrom
    def copyFrom(self, color):
        return self._setColor(color.asInt())

#___________________________________________________________________________________________________ load
    def load(self, value, normalized =False):
        return self._setColor(value, normalized=normalized)

#___________________________________________________________________________________________________ __str__
    def __str___(self):
        return self.asWeb

#___________________________________________________________________________________________________ asInt
    def asInt(self):
        return self._rawColor

#___________________________________________________________________________________________________ asWebRGBA
    def asWebRGBA(self, opacity =None):
        c = self.asRgb(output=tuple)
        return u'rgba(%s, %s, %s, %s)' % (
            unicode(c[0]),
            unicode(c[1]),
            unicode(c[2]),
            unicode(self._opacity if opacity is None else opacity) )

#___________________________________________________________________________________________________ asWebRgbOpacity
    def asWebRgbOpacity(self, opacity =None):
        c = self.asRgb(output=tuple)
        return u'rgba(%s, %s, %s, %s)' % (
            unicode(c[0]),
            unicode(c[1]),
            unicode(c[2]),
            unicode(100.0*(self._opacity if opacity is None else opacity)) + u'%' )

#___________________________________________________________________________________________________ asRgb
    def asRgb(self, normalize =False, output =None):
        if self._rgbColor is None:
            red   = self._rawColor >> 16
            green = (self._rawColor^self._rawColor >> 16 << 16) >> 8
            blue  = self._rawColor >> 8 << 8 ^ self._rawColor

            self._rgbColor = (red, green, blue)

            if normalize:
                red                = round(red/255.0)
                green              = round(green/255.0)
                blue               = round(blue/255.0)
                self._rgbNormColor = (red, green, blue)
        else:
            if normalize:
                red   = self._rgbNormColor[0]
                green = self._rgbNormColor[1]
                blue  = self._rgbNormColor[2]
            else:
                red   = self._rgbColor[0]
                green = self._rgbColor[1]
                blue  = self._rgbColor[2]

        if output is tuple:
            return red, green, blue
        elif output is list:
            return [red, green, blue]

        return {'r':red, 'g':green, 'b':blue}

#___________________________________________________________________________________________________ asHex
    def asHex(self):
        return hex(self._rawColor)

#___________________________________________________________________________________________________ asLuma
    def asLuma(self):
        if self._lumaColor is None:
            rgb = self.asRgb()
            self._lumaColor = (0.2126*rgb['r'] + 0.7152*rgb['g'] + 0.0722*rgb['b'])/255.0
        return self._lumaColor

#___________________________________________________________________________________________________ asWebAlpha
    def asWebAlpha(self):
        return hex(int(round(255.0*self._opacity))).replace('0x', '')

#___________________________________________________________________________________________________ asWebRgba
    def asWebRgba(self):
        return self.asWeb(compactify=False) + self.asWebAlpha()

#___________________________________________________________________________________________________ asWeb
    def asWeb(self, compactify =True):
        if compactify and not self._webCompactColor is None:
                return self._webCompactColor

        if not compactify and not self._webColor is None:
                return self._webColor

        res            = hex(self._rawColor).replace('0x','').upper()
        res            = '0'*(6 - len(res)) + res
        self._webColor = '#' + res

        if not compactify:
            return self._webColor

        l = len(res)
        if l == 6 and res == res[0]*2 + res[2]*2 + res[4]*2:
            res = res[0] + res[2] + res[4]
        elif l < 3:
            res += '0'*(3 - l)

        self._webCompactColor = '#' + res
        return self._webCompactColor

#___________________________________________________________________________________________________ asHsv
    def asHsv(self, normalize =False, output =None):
        out = None

        if normalize and not self._hsvNormColor is None:
            out = self._hsvNormColor

        if not normalize and not self._hsvColor is None:
            out = self._hsvColor

        if out is None:
            rgb = self.asRgb(output=tuple)
            r   = float(rgb[0])
            g   = float(rgb[1])
            b   = float(rgb[2])

            maxRGB     = max(r, g, b)
            minRGB     = min(r, g, b)
            hue        = 0

            #--- Hue ---#
            if maxRGB == minRGB:
                hue = 0
            elif maxRGB == r:
                hue = (60*(g - b)/(maxRGB - minRGB) + 360) % 360
            elif maxRGB == g:
                hue = (60*(b - r)/(maxRGB - minRGB) + 120)
            elif maxRGB == b:
                hue = (60*(r - g)/(maxRGB - minRGB) + 240)

            #--- Value ---#
            value = maxRGB

            #--- Saturation ---#
            if maxRGB == 0:
                saturation = 0
            else:
                saturation = (maxRGB - minRGB)/maxRGB

            if normalize:
                self._hsvNormColor = (hue/360.0, saturation, value/255.0)
                out                = self._hsvNormColor
            else:
                self._hsvColor = (hue, saturation*100.0, value/255.0*100.0)
                out            = self._hsvColor

        if output is tuple:
            return out
        elif output is list:
            return [out[0], out[1], out[2]]

        return {'h':out[0], 's':out[1], 'v':out[2]}

#___________________________________________________________________________________________________ asHsl
    def asHsl(self, normalize =False, output =None):
        out = None
        cls = self.__class__

        if normalize and not self._hslNormColor is None:
            out = self._hslNormColor

        if not normalize and not self._hslColor is None:
            out = self._hslColor

        if out is None:
            hsl = cls.rgbToHsl(self.asRgb())
            if normalize:
                hsl['h'] /= 360.0
                hsl['s'] /= 100.0
                hsl['l'] /= 100.0

            out = (hsl['h'], hsl['s'], hsl['l'])

            if normalize:
                self._hslNormColor = out
            else:
                self._hslColor = out

        if output is tuple:
            return out
        elif output is list:
            return [out[0], out[1], out[2]]

        return {'h':out[0], 's':out[1], 'l':out[2]}

#___________________________________________________________________________________________________ dodgeShift
    def dodgeShift(self, amount, maxAmount =None):
        c = self.asHsv()
        cls = self.__class__

        adjust = c['s'] - min(maxAmount if maxAmount else 100.0, amount*c['s'])
        c['s'] = cls.clamp(adjust, 0, 100)

        adjust = c['v'] + min(maxAmount if maxAmount else 100.0, amount*(100 - c['v']))
        c['v'] = cls.clamp(adjust, 0, 100)
        self._setColor(c)

#___________________________________________________________________________________________________ burnShift
    def burnShift(self, amount, maxAmount =None):
        c      = self.asHsv()
        coeff  = 1 - max(50 - c['s'], 0)/50
        adjust = c['s'] + min(maxAmount if maxAmount else 100.0, coeff*amount*(100 - c['s']))
        c['s'] = self.clamp(adjust, 0, 100)

        adjust = c['v'] - min(maxAmount if maxAmount else 100.0, amount*c['v'])
        c['v'] = self.clamp(adjust, 0, 100)
        self._setColor(c)

#___________________________________________________________________________________________________ rgbShift
    def rgbShift(self, r =0, g =0, b =0, normalized =False):
        c = self.asRgb()
        cls    = self.__class__
        factor = 255 if normalized else 1
        c['r'] = cls.clamp(c['r'] + factor*r, 0, 255)
        c['g'] = cls.clamp(c['g'] + factor*g, 0, 255)
        c['b'] = cls.clamp(c['b'] + factor*g, 0, 255)

        self._setColor(c)

#___________________________________________________________________________________________________ hsvShift
    def hsvShift(self, h =0, s =0, v =0, normalized =False, bounce =False):
        c = self.asHsv()
        cls    = self.__class__

        factor = 360 if normalized else 1
        c['h'] = (factor*h + c['h']) % 360

        factor = 100 if normalized else 1
        if bounce:
            c['s'] = cls.bounce(c['s'] + factor*s, 0, 100)
            c['v'] = cls.bounce(c['v'] + factor*v, 0, 100)
        else:
            c['s'] = cls.clamp(c['s'] + factor*s, 0, 100)
            c['v'] = cls.clamp(c['v'] + factor*v, 0, 100)

        self._setColor(c)

#___________________________________________________________________________________________________ hsvShift
    def hslShift(self, h =0, s =0, l =0, normalized =False, bounce =False):
        c = self.asHsl()
        cls    = self.__class__

        factor = 360 if normalized else 1
        c['h'] = (factor*h + c['h']) % 360

        factor = 100 if normalized else 1
        if bounce:
            c['s'] = cls.bounce(c['s'] + factor*s, 0, 100)
            c['l'] = cls.bounce(c['l'] + factor*l, 0, 100)
        else:
            c['s'] = cls.clamp(c['s'] + factor*s, 0, 100)
            c['l'] = cls.clamp(c['l'] + factor*l, 0, 100)

        self._setColor(c)

#___________________________________________________________________________________________________ bend
    def bend(self, bend):
        if not isinstance(bend, numbers.Number):
            bend = self.__class__.getBendCount(bend)

        if bend > 0:
            self.dodgeShift(float(bend)*0.25, 10*bend)
        else:
            bend = abs(bend)
            self.burnShift(float(bend)*0.25, 10*bend)

#___________________________________________________________________________________________________ clone
    def clone(self):
        return self.__class__(self._rawColor)

#___________________________________________________________________________________________________ hsvToRgb
    @classmethod
    def hsvToRgb(cls, hsv, normalized =False):
        r = 0.0
        g = 0.0
        b = 0.0

        h = float(hsv.get('h', 0.0))
        s = float(hsv.get('s', 0.0))
        v = float(hsv.get('v', 0.0))

        if normalized:
            h *= 360.0
            s *= 100.0
            v *= 100.0

        tempS   = s/100.0
        tempV   = v/100.0
        hi      = math.floor(h/60) % 6
        f       = h/60 - math.floor(h/60)
        p       = (tempV * (1 - tempS))
        q       = (tempV * (1 - f * tempS))
        t       = (tempV * (1 - (1 - f) * tempS))

        if hi == 0:
            r = tempV
            g = t
            b = p
        elif hi == 1:
            r = q
            g = tempV
            b = p
        elif hi == 2:
            r = p
            g = tempV
            b = t
        elif hi == 3:
            r = p
            g = q
            b = tempV
        elif hi == 4:
            r = t
            g = p
            b = tempV
        elif hi == 5:
            r = tempV
            g = p
            b = q

        return {'r':round(r*255.0), 'g':round(g*255.0), 'b':round(b*255.0)}

#___________________________________________________________________________________________________ hsvToInt
    @classmethod
    def hsvToInt(cls, hsv, normalized =False):
        return cls.rgbToInt(cls.hsvToRgb(hsv, normalized))

#___________________________________________________________________________________________________ rgbToInt
    @classmethod
    def rgbToInt(cls, rgb, normalized =False):
        try:
            r = float(rgb.get('r', 0.0))
            g = float(rgb.get('g', 0.0))
            b = float(rgb.get('b', 0.0))
        except Exception, err:
            try:
                r = float(rgb[0])
                g = float(rgb[1])
                b = float(rgb[2])
            except Exception, err:
                return 0

        if normalized:
            r *= 255.0
            g *= 255.0
            b *= 255.0

        return int(r) << 16 | int(g) << 8 | int(b)

#___________________________________________________________________________________________________ lumaToInt
    @classmethod
    def lumaToInt(cls, luma):
        value = round(luma*255.0)
        return cls.rgbToInt({'r':value, 'g':value, 'b':value})

#___________________________________________________________________________________________________ hexToInt
    @classmethod
    def hexToInt(cls, value):
        if not value[0] == '#' or value[0:1] == '0x':
            value = '#' + value
        return int(cls.formatHexColor(value), 16)

#___________________________________________________________________________________________________ rgbToHsl
    @classmethod
    def rgbToHsl(cls, rgb, normalized =False):
        r = float(rgb.get('r', 0.0))
        g = float(rgb.get('g', 0.0))
        b = float(rgb.get('b', 0.0))

        if not normalized:
            r /= 255.0
            g /= 255.0
            b /= 255.0

        maxC = max(r, g, b)
        minC = min(r, g, b)

        l = 0.5*(maxC + minC)

        if maxC == minC:
            return {'h':0.0, 's':0.0, 'l':100*l}

        d = maxC - minC
        s = d/(2.0 - maxC - minC) if l > 0.5 else d/(maxC + minC)
        if maxC == r:
            h = (g - b)/d + (6.0 if g < b else 0.0)
        elif maxC == g:
            h = (b - r)/d + 2.0
        else:
            h = (r - g)/d + 4.0
        h /= 6.0

        return {'h':360.0*h, 's':100.0*s, 'l':100*l}

#___________________________________________________________________________________________________ hslToRgb
    @classmethod
    def _hslToRgb(cls, hsl, normalized =False):
        h = float(hsl.get('h', 0.0))
        s = float(hsl.get('s', 0.0))
        l = float(hsl.get('l', 0.0))

        if not normalized:
            h /= 360.0
            s /= 100.0
            l /= 100.0

        if s == 0:
            rgb = round(255.0*l)
            return {'r':rgb, 'g':rgb, 'b':rgb}

        def hue2rgb(p, q, t):
            t += 1.0 if t < 0.0 else 0.0
            t -= 1.0 if t > 1.0 else 0.0
            if t < 1.0/6.0:
                return p + (q - p)*6.0*t
            if t < 1.0/2.0:
                return q
            if t < 2.0/3.0:
                return p + (q - p)*(2.0/3.0 - t)*6.0
            return p

        q = l*(1.0 + s) if l < 0.5 else l + s - l*s
        p = 2.0*l - q
        r = hue2rgb(p, q, h + 1.0/3.0)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1.0/3.0)

        return {'r':round(255.0*r), 'g':round(255.0*g), 'b':round(255.0*b)}

#___________________________________________________________________________________________________ hslToInt
    @classmethod
    def hslToInt(cls, hsl, normalized =False):
        return cls.rgbToInt(cls._hslToRgb(hsl, normalized))

#___________________________________________________________________________________________________ clamp
    @classmethod
    def clamp(cls, value, minValue =0, maxValue =1):
        return max(minValue, min(maxValue, value))

#___________________________________________________________________________________________________ bounce
    @classmethod
    def bounce(cls, value, minValue =0, maxValue =1):
        while value < minValue or value > maxValue:
            if value < minValue:
                value = minValue + (minValue - value)
            elif value > maxValue:
                value = maxValue - (value - maxValue)
            else:
                break

        return value

#___________________________________________________________________________________________________ isHexColor
    @classmethod
    def isHexColor(cls, value):
        value = value.replace('#','').replace('0x','')
        if len(value) != 6 and len(value) != 3:
            return False

        return cls._HEX_COLOR_PATTERN.search(value) is None

#___________________________________________________________________________________________________ formatHexColor
    @classmethod
    def formatHexColor(cls, value, forWeb =False):
        value = value.replace('#','').replace('0x','')
        if len(value) == 3:
            value = value[0]*2 + value[1]*2 + value[2]*2
        return ('#' if forWeb else '0x') + value

#___________________________________________________________________________________________________ getBendCount
    @classmethod
    def getBendCount(cls, source):
        res = cls._BEND_FINDER.search(source)
        if res:
            cBend = 0
            bends = res.group()
            for i in range(len(bends)):
                cBend += 1 if bends[i:i+1] == '+' else -1
            return max(-3, min(3, cBend))
        else:
            return 0

#___________________________________________________________________________________________________ fromIntRgb
    @classmethod
    def fromIntRgb(cls, value, alpha =1.0):
        return cls.createDict(color=int(value), alpha=alpha)

#___________________________________________________________________________________________________ fromIntRgb
    @classmethod
    def fromIntRgba(cls, value):
        color = int(value) >> 8
        alpha = float(int(value) & 0xFF)/255.0
        return cls.createDict(color=color, alpha=alpha)

#___________________________________________________________________________________________________ fromIntRgb
    @classmethod
    def fromHexRgb(cls, value, alpha =1.0):
        return cls.createDict(color=int(value, 8), alpha=alpha)

#___________________________________________________________________________________________________ fromIntRgb
    @classmethod
    def fromHexRgba(cls, value):
        color = int(value, 8) >> 8
        alpha = float(int(value, 8) & 0xFF)/255.0
        return cls.createDict(color=value, alpha=alpha)

#___________________________________________________________________________________________________ fromWebRgba
    @classmethod
    def fromWebRgba(cls, value):
        pass

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _setColor
    def _setColor(self, sourceColor, normalized =False):
        bendCount = None
        cls       = self.__class__

        # COLOR VALUE DICT
        if isinstance(sourceColor, dict) and 'color' in sourceColor:
            self.fromDict(sourceColor)

        # INTEGER COLOR
        elif isinstance(sourceColor, int) or isinstance(sourceColor, long):
            self._rawColor = int(sourceColor)

        # FLOAT LUMA COLOR
        elif isinstance(sourceColor, float):
            self._rawColor = cls.lumaToInt(sourceColor)

        # RGB, HSV, OR HSL DICT COLOR
        elif isinstance(sourceColor, dict):
            for key in ['a', 'alpha', 'o', 'opacity']:
                if key in sourceColor:
                    self._opacity = float(sourceColor[key])
                    break

            if 'l' in sourceColor:
                self._rawColor = cls.hslToInt(sourceColor, normalized)
            if 'h' in sourceColor or 's' in sourceColor or 'v' in sourceColor:
                self._rawColor = cls.hsvToInt(sourceColor, normalized)
            else:
                self._rawColor = cls.rgbToInt(sourceColor, normalized)

        # RGB TUPLE OR LIST COLOR
        elif isinstance(sourceColor, tuple) or isinstance(sourceColor, list):
            r      = sourceColor[0]
            g      = sourceColor[1]
            b      = sourceColor[2]
            factor = 255.0 if normalized else 1.0
            c      = {'r':round(factor*r), 'g':round(factor*g), 'b':round(factor*b)}
            self._rawColor = cls.rgbToInt(c)

            if len(sourceColor) > 3:
                self._opacity = float(sourceColor[3])

        # STRING-BASED COLORS
        elif isinstance(sourceColor, basestring):
            bendCount   = cls.getBendCount(sourceColor)
            sourceColor = sourceColor.rstrip('+-')

            if cls.isHexColor(sourceColor):
                self._rawColor = cls.hexToInt(sourceColor)
            else:
                self._rawColor = self._parseUnknownColorString(sourceColor)
                if self._rawColor is None:
                    self._rawColor = 0

        # IF ALL ELSE FAILS: BLACK!
        else:
            self._rawColor = 0

        # CLEAR THE COLOR CACHE
        self._unCache()

        # IF STRING COLOR BEND
        if bendCount:
            self.bend(bendCount)

#___________________________________________________________________________________________________ _unCache
    def _unCache(self):
        self._hslColor              = None
        self._hslNormColor          = None
        self._rgbColor              = None
        self._rgbNormColor          = None
        self._hsvColor              = None
        self._hsvNormColor          = None
        self._webColor              = None
        self._webCompactColor       = None
        self._lumaColor             = None
        self._shiftUpColors         = None
        self._shiftDownColors       = None

#___________________________________________________________________________________________________ _getWebValue
    def _getWebValue(self, compact):
        if compact and not self._webCompactColor is None:
            return self._webCompactColor

        if not compact and not self._webColor is None:
            return self._webColor

        return self.asWeb(compact)

#___________________________________________________________________________________________________ _getRGBValue
    def _getRGBValue(self, index, normalize):
        if normalize and not self._rgbNormColor is None:
            return self._rgbNormColor[index]

        if not normalize and not self._rgbColor is None:
            return self._rgbColor[index]

        c = self.asRgb(normalize, tuple)
        return c[index]

#___________________________________________________________________________________________________ _getHSVValue
    def _getHSVValue(self, index, normalize):
        if normalize and not self._hsvNormColor is None:
            return self._hsvNormColor[index]

        if not normalize and not self._hsvColor is None:
            return self._hsvColor[index]

        c = self.asHsv(normalize, tuple)
        return c[index]

#___________________________________________________________________________________________________ _getHSLValue
    def _getHSLValue(self, index, normalize):
        if normalize and not self._hslNormColor is None:
            return self._hslNormColor[index]

        if not normalize and not self._hslColor is None:
            return self._hslColor[index]

        c = self.asHsl(normalize, tuple)
        return c[index]

#___________________________________________________________________________________________________ _parseUnknownColorString
    def _parseUnknownColorString(self, value):
        from pyaid.color.ColorNames import ColorNames
        value = value.strip().lower().replace(u' ', u'')
        if value in ColorNames.CLEAN_NAMES:
            return ColorNames.CLEAN_NAMES[value]
        return None
