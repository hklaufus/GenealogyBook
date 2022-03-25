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


class Section(pl.Section):
    """A class that represents a section."""

    marker_prefix = "sec"


class Subsection(pl.Section):
    """A class that represents a subsection."""

    marker_prefix = "subsec"


class Subsubsection(pl.Section):
    """A class that represents a subsubsection."""

    marker_prefix = "ssubsec"


class Paragraph(pl.Section):
    """A class that represents a paragraph."""

    marker_prefix = "para"


class Subparagraph(pl.Section):
    """A class that represents a subparagraph."""

    marker_prefix = "subpara"

class Figure(pl.Figure):
    """A class that represents a Figure environment."""

    # 20211127: Remove 'fix_filename'
    def add_image(self, filename, *, width=pl.NoEscape(r'0.8\textwidth'), placement=pl.NoEscape(r'\centering')):
        """Add an image to the figure.
        Args
        ----
        filename: str
            Filename of the image.
        width: str
            The width of the image
        placement: str
            Placement of the figure, `None` is also accepted.
        """

        if width is not None:
            if self.escape:
                width = pu.escape_latex(width)

            width = 'width=' + str(width)

        if placement is not None:
            self.append(placement)

        self.append(pl.StandAloneGraphic(image_options=width, filename=filename))


class WrapFigure(pl.base_classes.Environment):
    """A class to wrap LaTeX's wrapfig environment."""  # [lineheight]{position}{width}

    packages = [pl.package.Package('wrapfig')]
    escape = False
    content_separator = "\n"


def GetPersonNameWithReference(pGivenNames, pSurname, pGrampsId):
    return r'\personref[chap:' + pGrampsId + ']{' + pGivenNames + " " + pSurname + '}'


def CreateSubLevel(pLevel=Chapter, pTitle="Title", pLabel=False):
    if(type(pLevel) is Part):
        # Current level is Part, create Chapter
        vSubLevel = pLevel.create(Chapter(title=pTitle, label=pLabel))

    elif(type(pLevel) is Chapter):
        # Current level is Chapter, create Section
        vSubLevel = pLevel.create(Section(title=pTitle, label=pLabel))

    elif(type(pLevel) is Section):
        # Current level is Section, create Subsection
        vSubLevel = pLevel.create(Subsection(title=pTitle, label=pLabel))

    elif(type(pLevel) is Subsection):
        # Current level is Subsection, create Subsubsection
        vSubLevel = pLevel.create(Subsubsection(title=pTitle, label=pLabel))

    elif(type(pLevel) is Subsubsection):
        # Current level is Subsubsection, create Paragraph
        vSubLevel = pLevel.create(Paragraph(title=pTitle, label=pLabel))

    elif(type(pLevel) is Paragraph):
        # Current level is Paragraph, create Subparagraph
        vSubLevel = pLevel.create(Subparagraph(title=pTitle, label=pLabel))

    elif(type(pLevel) is Subparagraph):
        # Current level is Subparagraph, no further level down
        pass

    else:
       print("ERROR in hkLatex.CreateSubLevelTextPart: pLevel not recognised: ", type(pLevel)) 

    return vSubLevel
