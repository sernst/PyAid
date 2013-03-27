# RadixConverter.py
# (C)2012
# Scott Ernst

import sys
import getopt

from pyaid.radix.Base64 import Base64
from pyaid.radix.Base36 import Base36

#___________________________________________________________________________________________________ RadixConverter
class RadixConverter(object):
    """A class for..."""

#===================================================================================================
#                                                                                     P U B L I C

#___________________________________________________________________________________________________ from64
    @classmethod
    def from64(self, value):
        """Doc..."""
        return Base64.from64(value, True)

#___________________________________________________________________________________________________ to64
    @classmethod
    def to64(self, value):
        """Doc..."""
        return Base64.to64(int(value))

#___________________________________________________________________________________________________ from36
    @classmethod
    def from36(self, value):
        """Doc..."""
        return Base36.from36(value, True)

#___________________________________________________________________________________________________ to36
    @classmethod
    def to36(self, value):
        """Doc..."""
        return Base36.to36(int(value))

#===================================================================================================
#                                                                               P R O T E C T E D

#___________________________________________________________________________________________________ _internalMethod
    def _internalMethod(self):
        """Doc..."""
        pass

####################################################################################################
####################################################################################################

#___________________________________________________________________________________________________ usage
def usage():
    print """
    Convenience class for calling radix conversion methods.
        --from64        - Prints the specified base 64 string converted into base 10.
        --to64          - Prints the specified base 10 integer converted into base 64.
        --from36        - Prints the specified base 36 string converted into base 10.
        --to36          - Prints the specified base 10 integer converted into base 36.
    """

#___________________________________________________________________________________________________ main
def main():
    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:],
            "h",
            ["help", 'from64=', 'to64=', 'from36=', 'to36=']
        )
    except getopt.GetoptError, err:
        print str(err) + "\n"
        usage()
        sys.exit(2)

    inRadix  = None
    outRadix = None
    input    = None
    out      = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ('--from64'):
            input = a.strip()
            inRadix  = '64'
            outRadix = '10'
            out = RadixConverter.from64(input)
        elif o in ('--to64'):
            input = a.strip()
            inRadix  = '10'
            outRadix = '64'
            out = RadixConverter.to64(int(input))
        elif o in ('--from36'):
            input = a.strip()
            inRadix  = '36'
            outRadix = '10'
            out = RadixConverter.from36(input)
        elif o in ('--to36'):
            input = a.strip()
            inRadix  = '10'
            outRadix = '36'
            out = RadixConverter.to36(int(input))
        else:
            print "\nUnknown argument: " + o + ". Unable to continue.\n\n"
            usage()
            sys.exit(2)

    print '\n\tConverted from base %s to base %s:' % (inRadix, outRadix)
    print '\t  INPUT: ' + str(input)
    print '\t  VALUE: ' + str(out)
    print ''

####################################################################################################
####################################################################################################

if __name__ == '__main__':
    main()

