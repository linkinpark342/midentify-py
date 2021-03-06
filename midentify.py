"""
Get video information from a file using mplayer's midentify script

The function you want is midentify

@author Abhishek Mukherjee
@email linkinpark342@gmail.com
"""

from subprocess import Popen, PIPE
import re
import ast

MIDENTIFY_CMD = 'midentify'

PAIR_REGEX = re.compile(r"^(?P<key>[^=\n]+)=(?P<value>(\\\n|.)*)$",
        flags=re.MULTILINE)
UNESCAPE_REGEX = re.compile(r"\\(.)", flags=re.DOTALL)

class MidentifyFile(object):

    """
    Holds the metadata for a movie file created by midentify() call. Keys for
    the metadata can be accessed either through [] or simple . notation and
    will be named after their midentify counterparts, lowercased, with ID_
    removed from the beginning
    
    >>> f = MidentifyFile("ID_VIDEO_WIDTH=1920\\nID_VIDEO_HEIGHT=1080")
    >>> f.video_width
    1920
    >>> f.video_height
    1080
    """

    def __init__(self, information_string):
        """ Create an object based on output from midentify

        information_string should be similar to:

        ID_VIDEO_WIDTH=1920
        ID_VIDEO_HEIGHT=1080

        """
        self.keys = []
        for match in PAIR_REGEX.finditer(information_string):
            key = match.groupdict()['key']
            value = UNESCAPE_REGEX.sub(lambda m: m.groups()[0],
                    match.groupdict()['value'])
            value = self._guess_type(value)
            key = key.lower().lstrip('id_')
            self.__dict__[key] = value
            self.keys.append(key)

    @staticmethod
    def _guess_type(val):
        """ Try to interpret a result from midentify

        >>> MidentifyFile._guess_type("5")
        5
        >>> MidentifyFile._guess_type("5.5")
        5.5
        >>> MidentifyFile._guess_type("foo") == unicode('foo')
        True

        """
        try:
            return ast.literal_eval(val)
        except Exception:
            return unicode(val)

    def __getitem__(self, key):
        if key not in self.keys:
            return None
        return self.__dict__[key]

    def __iter__(self):
        for key in self.keys:
            yield (key, self[key])


def midentify(filename):
    """Returns a MidentifyFile object for the file at filename"""
    output = Popen([MIDENTIFY_CMD, filename], stdout=PIPE).communicate()[0]
    return MidentifyFile(output)

def _test():
    """
    Tests this module
    """
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
    
