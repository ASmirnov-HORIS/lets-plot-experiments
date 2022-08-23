from collections import namedtuple

# Classes

class FontFace(namedtuple("FontFace", ["bold", "italic"])):
    __slots__ = ()
    def __str__(self):
        if self.bold and self.italic:
            return "bold+italic"
        elif self.bold and not self.italic:
            return "bold"
        elif not self.bold and self.italic:
            return "italic"
        else:
            return "normal"

Font = namedtuple("Font", ["family", "size", "face"])

# Constants

FONT_FAMILIES = [
    "Courier",
    "Geneva",
    "Georgia",
    "Helvetica",
    "Lucida Grande",
    "Times New Roman",
    "Verdana",
    "Arial",
    "Lucida Console",
]

FONT_SIZES = [9, 11, 12, 14, 16, 20]

FONT_FACES = [
    FontFace(False, False),
    FontFace(True, False),
    FontFace(False, True),
    FontFace(True, True),
]

BASIC_FONT_FAMILY = "Lucida Grande"
BASIC_FONT_SIZE = 14
BASIC_FONT_FACE = FontFace(False, False)
BASIC_FONT = Font(BASIC_FONT_FAMILY, BASIC_FONT_SIZE, BASIC_FONT_FACE)

# Functions

def is_monospaced(font):
    if isinstance(font, str):
        if font in ["Courier", "Lucida Console"]:
            return True
        elif font in ["Geneva", "Georgia", "Helvetica", "Lucida Grande", "Times New Roman", "Verdana", "Arial"]:
            return False
        else:
            raise Exception("Unknown font face: {0}.".format(font))
    elif isinstance(font, Font):
        return is_monospaced(font.family)
    else:
        raise TypeError("Only Font and str are allowed.")