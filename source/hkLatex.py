# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc


class Part(pl.Section):
    """A class that represents a part."""

    marker_prefix = "part"


class Chapter(pl.Section):
    """A class that represents a chapter."""

    marker_prefix = "chap"


class WrapFigure(pl.base_classes.Environment):
    """A class to wrap LaTeX's wrapfig environment."""  # [lineheight]{position}{width}

    packages = [pl.package.Package('wrapfig')]
    escape = False
    content_separator = "\n"


def GetPersonNameWithReference(pGivenNames, pSurname, pGrampsId):
    return r'\personref[chap:' + pGrampsId + \
        ']{' + pGivenNames + " " + pSurname + '}'
