import logging
import sys

import ahnentafel_chapter
import person_chapter

import gramps_db
import language
import latex

from pathlib import Path
import pylatex as pl # https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex.utils as pu
import xml.dom.minidom as mdm

class Book:
    __writer__: str = '<Author>'
    __title__: str = '<Title>'
    __file_name__: str = None
    __start_person_id__: str = None
    __language__: str = 'nl'
    __book_path__: str = '../book/'
    __chapter_path__: str = '../book/chapter/'
    __figure_path__: str = '../book/figures/'
    __life_sketch_path__: str = '../book/life_sketches/'
    __appendix_path__: str = '../book/appendices/'
    __exclude__: list[str] = None
    __appendix__: list[str] = None

    def __init__(self, p_config_file = '../config/config.xml'):
        # Check if config file exists
        v_file = Path(p_config_file)
        if not v_file.exists():
            logging.warning(f'Configuration file "{v_file}" does not exist. Current working directory: {Path.cwd()}')
            sys.exit('Aborting programme')

        else:
            self.read_config_xml(p_config_file)

        # Check if folders exist
        for v_item in [self.__book_path__, self.__chapter_path__, self.__figure_path__, self.__life_sketch_path__, self.__appendix_path__]:
            v_path_1 = Path.cwd()
            v_path_2 = Path(v_item)
            v_path = v_path_1.joinpath(v_path_2).resolve()
            if not v_path.exists():
                v_path.mkdir()


    def read_config_xml(self, p_file_name):
        """
        Reads a config file with default parameters

        :param p_file_name:
        :return:
        """

        v_dom = mdm.parse(p_file_name)

        self.__writer__ = v_dom.getElementsByTagName('Author')[0].childNodes[0].nodeValue
        self.__title__ = v_dom.getElementsByTagName('Title')[0].childNodes[0].nodeValue
        self.__file_name__ = v_dom.getElementsByTagName('Filename')[0].childNodes[0].nodeValue
        self.__start_person_id__ = v_dom.getElementsByTagName('StartPersonId')[0].childNodes[0].nodeValue
        self.__language__ = v_dom.getElementsByTagName('Language')[0].childNodes[0].nodeValue
        self.__book_path__ = v_dom.getElementsByTagName('BookPath')[0].childNodes[0].nodeValue
        self.__chapter_path__ = v_dom.getElementsByTagName('ChapterPath')[0].childNodes[0].nodeValue
        self.__figure_path__ = v_dom.getElementsByTagName('FiguresPath')[0].childNodes[0].nodeValue
        self.__life_sketch_path__ = v_dom.getElementsByTagName('LifeSketchPath')[0].childNodes[0].nodeValue
        self.__appendix_path__ = v_dom.getElementsByTagName('AppendixPath')[0].childNodes[0].nodeValue
        self.__exclude__ = v_dom.getElementsByTagName('Exclude')[0].childNodes[0].nodeValue.split(';')
        self.__appendix__ = v_dom.getElementsByTagName('Appendix')[0].childNodes[0].nodeValue.split(';')


    def __write_preamble(self, p_document: pl.Document) -> None:
        """
        Write the pre-amble of the document

        :param p_document:
        :return:
        """

        #
        # Packages
        #

        # v_document.packages.append(pl.Package('lipsum'))
        p_document.packages.append(pl.Package('blindtext'))
        p_document.packages.append(pl.Package('hyperref'))

        # https://tex.stackexchange.com/questions/118602/how-to-text-wrap-an-image-in-latex#132313
        p_document.packages.append(pl.Package('graphicx'))
        p_document.packages.append(pl.Package('wrapfig'))
        p_document.packages.append(pl.Package('tocloft'))
        p_document.packages.append(pl.Package('needspace'))

        # The next packages are inserted automatically by PyLaTeX??
        p_document.packages.append(pl.Package('tabu'))
        p_document.packages.append(pl.Package('longtable'))

        # Packages to scale images
        p_document.packages.append(pl.Package('scalerel'))
        p_document.packages.append(pl.Package('fp'))
        p_document.packages.append(pl.Package('caption'))  # for figure captions outside a float environment

        # Packages to trim images
        p_document.packages.append(pl.Package('adjustbox'))

        # Package to handle pdf pages
        p_document.packages.append(pl.Package('pdfpages'))

        # Packages to ensure floats stay inside section
        p_document.packages.append(pl.Package('placeins'))  # allows for \floatbarrier

        # Packages for coloring text
        p_document.packages.append(pl.Package('xcolor'))

        # Packages for TikZ
        p_document.packages.append(pl.Package('tikz'))

        #
        # Preamble
        #
        p_document.preamble.append(pl.NoEscape(r'\makeatletter'))
        p_document.preamble.append(pl.NoEscape(r'\newcommand{\personref}[2][I9999]{\@ifundefined{r@#1}{#2}{\hyperref[#1]{#2}$_{/\pageref{#1}/}$}}'))
        p_document.preamble.append(pl.NoEscape(r'\newcommand{\minspace}{5\baselineskip}'))

        # To get the integer part from a floating value
        p_document.preamble.append(pl.NoEscape(r'\newcommand{\intpart}[1]{\expandafter\int@part#1..\@nil}'))
        p_document.preamble.append(pl.NoEscape(r'\def\int@part#1.#2.#3\@nil{\if\relax#1\relax0\else#1\fi}'))
        p_document.preamble.append(pl.NoEscape(r'\makeatother'))

        # Only show levels up to Chapter in Table of Contents
        p_document.preamble.append(pl.NoEscape(r'\setcounter{tocdepth}{0}'))

        # Increase number width to prevent chapter numbers and heading titles from overlapping in the toc
        p_document.preamble.append(pl.NoEscape(r'\advance\cftchapnumwidth 1.0em\relax'))
        p_document.preamble.append(pl.NoEscape(r'\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}'))

        # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height
        p_document.preamble.append(pl.NoEscape(r'\newsavebox\x'))
        p_document.preamble.append(pl.NoEscape(r'\newcount\widthImages'))
        p_document.preamble.append(pl.NoEscape(r'\newcount\widthAvailable'))

        # Counters for filling up wrapfigure in hkPersonChapter
        p_document.preamble.append(pl.NoEscape(r'\newcounter{maxlines}'))
        p_document.preamble.append(pl.NoEscape(r'\newcounter{mycounter}'))

        # Redefine labels fo chapters
        p_document.preamble.append(pl.NoEscape(r'\renewcommand{\contentsname}{' + language.translate('table of contents') + '}'))
        p_document.preamble.append(pl.NoEscape(r'\renewcommand{\listfigurename}{' + language.translate('list of figures') + '}'))
        p_document.preamble.append(pl.NoEscape(r'\renewcommand{\partname}{' + language.translate('generation') + '}'))
        p_document.preamble.append(pl.NoEscape(r'\renewcommand{\chaptername}{' + language.translate('chapter') + '}'))

        p_document.preamble.append(pl.Command('title', self.__title__))
        p_document.preamble.append(pl.Command('author', self.__writer__))
        p_document.preamble.append(pl.Command('date', pu.NoEscape(r'\today')))

        # Define TikZ styles
        p_document.append(pu.NoEscape(r'\usetikzlibrary{arrows.meta, graphs}'))
        p_document.append(pu.NoEscape(r'\tikzset{thick, black!50, text=black}'))
        p_document.append(pu.NoEscape(r'\tikzset{>={Stealth[round]}}'))
        p_document.append(pu.NoEscape(r'\tikzset{graphs/every graph/.style={edges=rounded corners}}'))
        p_document.append(pu.NoEscape(r'\tikzset{point/.style={circle,inner sep=0pt,minimum size=5pt,fill=red}}'))
        p_document.append(pu.NoEscape(r'\tikzset{terminal/.style={circle,minimum size=6mm,very thick,draw=black!50,top color=white,bottom color=black!20,font=\ttfamily}}'))
        p_document.append(pu.NoEscape(r'\tikzset{date/.style={rectangle,rounded corners=3mm,minimum size=6mm,very thick,draw=green!50,top color=white,bottom color=green!50!black!20,font=\ttfamily}}'))
        p_document.append(pu.NoEscape(r'\tikzset{self/.style={thick,double}}'))
        p_document.append(pu.NoEscape(r'\tikzset{man/.style={rectangle,thick,draw=blue!50!black!50,top color=white, bottom color=blue!50!black!20,rounded corners=.8ex}}'))
        p_document.append(pu.NoEscape(r'\tikzset{woman/.style={rectangle,thick,draw=red!50!black!50,top color=white,bottom color=red!50!black!20,rounded corners=.8ex}}'))
        p_document.append(pu.NoEscape(r'\tikzset{left/.style={xshift=-2.5mm,anchor=east, minimum size=6mm}}'))
        p_document.append(pu.NoEscape(r'\tikzset{right/.style={xshift=2.5mm,anchor=west, minimum size=6mm}}'))
        p_document.append(pu.NoEscape(r'\tikzset{vh path/.style={to path={|- (\tikztotarget)}}}'))

        p_document.append(pu.NoEscape(r'\maketitle'))
        p_document.append(pl.Command('tableofcontents'))


    def __write_body(self, p_document: pl.Document, p_cursor) -> None:
        """
        Write the body of the document

        :param p_document:
        :param p_cursor:
        :return:
        """

        # Find handle of root person
        v_person_handle = gramps_db.get_person_handle_by_gramps_id(self.__start_person_id__, p_cursor)

        # If chapter path is sub-folder of book path, then create a relative path
        v_chapter_path = self.__chapter_path__.replace(self.__book_path__, './')
        # v_figure_path = self.__figure_path__.replace(self.__book_path__, './')
        # v_life_sketch_path = self.__life_sketch_path__.replace(self.__book_path__, './')

        if v_person_handle is not None:
            # Write the Ahnentafel of this person
            v_ahnentafel = ahnentafel_chapter.Ahnentafel(v_person_handle, p_cursor, self.__chapter_path__, True)
            v_ahnentafel.create_ahnentafel_chapter()
            # v_document.append(pl.NoEscape(r'\include{' + self.__chapter_path__ + 'Ahnentafel}'))
            p_document.append(pl.NoEscape(r'\include{' + v_chapter_path + 'Ahnentafel}'))

            #
            # Build a book consisting of parts for each generation.
            # Each part will contain chapters for all persons in the Ahnentafel
            #
            v_multi_generation_list = v_ahnentafel.__generation_list__

            # Create sub list for first generation
            v_generation_index = 1
            v_generation_list = [x[0] for x in v_multi_generation_list if x[1] == v_generation_index]

            while len(v_generation_list) > 0:
                # Create a new part for this generation
                # v_part = hkLatex.Part(title=language.translate('generation') + ' ' + str(v_generation_index), label=False)
                v_part = latex.Part(title=' ', label=False)
                v_part.generate_tex(filepath=self.__chapter_path__ + 'Part_' + str(v_generation_index))

                # Include the part to the document
                # v_document.append(pl.NoEscape(r'\include{' + self.__chapter_path__ + 'Part_' + str(v_generation_index) + '} % Generation ' + str(v_generation_index)))
                p_document.append(pl.NoEscape(r'\include{' + v_chapter_path + 'Part_' + str(v_generation_index) + '} % Generation ' + str(v_generation_index)))

                # Create a detailed chapter for each person in this generation
                for v_person_handle in v_generation_list:
                    v_person_chapter = person_chapter.PersonChapter(p_person_handle=v_person_handle,
                                                                    p_cursor=p_cursor,
                                                                    p_chapter_path=self.__chapter_path__,
                                                                    p_figures_path=self.__figure_path__,
                                                                    p_life_sketch_path=self.__life_sketch_path__,
                                                                    p_language=self.__language__)
                    v_person = v_person_chapter.get_person()

                    if v_person.get_gramps_id() in self.__exclude__:
                        logging.info(f"SKIPPING a chapter about: {v_person.__given_names__} {v_person.__surname__}")
                    else:
                        v_person_chapter.write_person_chapter()
                        # v_document.append(pl.NoEscape(r'\include{' + self.__chapter_path__ + v_person.__gramps_id__ + '} % ' + v_person.__given_names__ + ' ' + v_person.__surname__))
                        p_document.append(pl.NoEscape(r'\include{' + v_chapter_path + v_person.__gramps_id__ + '} % ' + v_person.__given_names__ + ' ' + v_person.__surname__))

                #  Create new sub list for next generation
                v_generation_index = v_generation_index + 1
                v_generation_list = [x[0] for x in v_multi_generation_list if x[1] == v_generation_index]


    def __write_appendices(self, p_document: pl.Document) -> None:
        """
        Write the appendices of the document

        :param p_document:
        :return:
        """

        # If appendix path is sub-folder of book path, then create a relative path
        v_appendix_path = self.__appendix_path__.replace(self.__book_path__, './')

        if len(self.__appendix__) > 0:
            p_document.append(pl.NoEscape(r'\appendix'))
            for v_appendix in self.__appendix__:
                # v_document.append(pl.NoEscape(r'\include{' + self.__chapter_path__ + v_appendix + '}'))
                p_document.append(pl.NoEscape(r'\include{' + v_appendix_path + v_appendix + '}'))


    def write_main_document(self, p_cursor):
        # vGeometryOptions = ["tmargin": "1cm", "lmargin": "10cm"]
        v_document_options = ['hidelinks', '10pt', 'a4paper', 'titlepage']
        v_document = pl.Document(documentclass='book', document_options=v_document_options)

        self.__write_preamble(p_document=v_document)
        self.__write_body(p_document=v_document, p_cursor=p_cursor)
        self.__write_appendices(p_document=v_document)


        # Write the book
        v_document.generate_tex(filepath=self.__book_path__ + self.__file_name__)
