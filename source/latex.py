# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu


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


def get_person_name_with_reference(p_given_names, p_surname, p_gramps_id):
    return r'\personref[chap:' + p_gramps_id + ']{' + p_given_names + " " + p_surname + '}'


def create_sub_level(p_level=Chapter, p_title="Title", p_label=False):
    if type(p_level) is Part:
        # Current level is Part, create Chapter
        v_sub_level = p_level.create(Chapter(title=p_title, label=p_label))

    elif type(p_level) is Chapter:
        # Current level is Chapter, create Section
        v_sub_level = p_level.create(Section(title=p_title, label=p_label))

    elif type(p_level) is Section:
        # Current level is Section, create Subsection
        v_sub_level = p_level.create(Subsection(title=p_title, label=p_label))

    elif type(p_level) is Subsection:
        # Current level is Subsection, create Subsubsection
        v_sub_level = p_level.create(Subsubsection(title=p_title, label=p_label))

    elif type(p_level) is Subsubsection:
        # Current level is Subsubsection, create Paragraph
        v_sub_level = p_level.create(Paragraph(title=p_title, label=p_label))

    elif type(p_level) is Paragraph:
        # Current level is Paragraph, create Subparagraph
        v_sub_level = p_level.create(Subparagraph(title=p_title, label=p_label))

    elif type(p_level) is Subparagraph:
        # The current level is Subparagraph, no further level down
        pass

    else:
       print("ERROR in hkLatex.CreateSubLevelTextPart: p_level not recognised: ", type(p_level))

    return v_sub_level
