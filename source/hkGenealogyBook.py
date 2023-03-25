import sqlite3
# import os
import logging

import hkLanguage as hlg
import hkPersonChapter as hpc
import hkGrampsDb as hgd
import hkAhnentafelChapter as hac
import hkLatex as hlt

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc

import xml.dom.minidom as mdm


def read_config_xml(p_file_name='config.xml'):
    v_book_parameters = {}
    v_book_parameters['Author'] = '<Author>'
    v_book_parameters['Title'] = '<Title>'
    v_book_parameters['Filename'] = '<Filename>'
    v_book_parameters['StartPersonId'] = 'I0000'
    v_book_parameters['Language'] = 'nl'
    v_book_parameters['Path'] = '../book/'

    # Filter is used only for children; parents will always be separately described
    v_book_parameters['Filter'] = ['Surname1', 'Surname2']

    v_dom = mdm.parse(p_file_name)

    v_book_parameters['Author'] = v_dom.getElementsByTagName('Author')[0].childNodes[0].nodeValue
    v_book_parameters['Title'] = v_dom.getElementsByTagName('Title')[0].childNodes[0].nodeValue
    v_book_parameters['Filename'] = v_dom.getElementsByTagName('Filename')[0].childNodes[0].nodeValue
    v_book_parameters['StartPersonId'] = v_dom.getElementsByTagName('StartPersonId')[0].childNodes[0].nodeValue
    v_book_parameters['Language'] = v_dom.getElementsByTagName('Language')[0].childNodes[0].nodeValue
    v_book_parameters['Path'] = v_dom.getElementsByTagName('Path')[0].childNodes[0].nodeValue

    # Debug
    # logging.debug("v_book_parameters: ".join(map(str, v_book_parameters)))

    return v_book_parameters


def process_person(p_person_handle, p_cursor, p_document, p_document_path, p_done_list):
    if p_person_handle not in p_done_list:
        # Add person to Done list to prevent of processing twice
        p_done_list.append(p_person_handle)

        v_person = hpc.Person(p_person_handle, p_cursor)

        if v_person.gramps_id is not None:
            # Fetch parents + children
            v_process_list = []
            v_process_list.append(v_person.father_handle)
            v_process_list.append(v_person.mother_handle)

            if len(v_filter) > 0:  # TODO: v_filter not defined
                # Only persons with relation to vStartPersonId and surnames as per filter
                for v_child_handle in v_person.children_handles_list:
                    v_child = hpc.Person(v_child_handle, p_cursor)
                    if v_child.surname in v_filter:
                        v_process_list.append(v_child.person_handle)
            else:
                # Anyone in database with relation to vStartPersonId
                v_process_list = v_process_list + v_person.children_handles_list

            # Create chapter in sub-document describing current person
            p_document.append(pl.NoEscape(r'\include{' + v_person.gramps_id + '} % ' + v_person.given_names + ' ' + v_person.surname))
            v_person.write_person_chapter()

            # Process stack
            for v_next_person in v_process_list:
                if v_next_person is not None:
                    process_person(v_next_person, p_cursor, p_document, p_document_path, p_done_list)
                # else:
                #     print('ERROR fetching v_next_person')
                #     print("v_next_person: ", v_next_person)
        else:
            print('ERROR fetching v_person.GrampsId')
            print("v_person.GrampsId: ", v_person.gramps_id)


def write_main_document(p_cursor, p_book_parameters):
    # vGeometryOptions = {"tmargin": "1cm", "lmargin": "10cm"}
    v_document_options = {'hidelinks', '10pt', 'a4paper', 'titlepage'}
    # v_document_options = {'10pt', 'a4paper', 'titlepage'}
    v_document = pl.Document(documentclass='book', document_options=v_document_options)

    #
    # Packages
    #

    # v_document.packages.append(pl.Package('lipsum'))
    v_document.packages.append(pl.Package('blindtext'))
    v_document.packages.append(pl.Package('hyperref'))
    # v_document.packages.append(pl.Package('graphicx'))  # TODO: Check no longer needed??

    # https://tex.stackexchange.com/questions/118602/how-to-text-wrap-an-image-in-latex#132313
    v_document.packages.append(pl.Package('wrapfig'))
    v_document.packages.append(pl.Package('tocloft'))
    v_document.packages.append(pl.Package('needspace'))

    # The next packages should be automatically inserted by PyLaTeX??
    v_document.packages.append(pl.Package('tabu'))
    v_document.packages.append(pl.Package('longtable'))

    # Packages to scale images
    v_document.packages.append(pl.Package('scalerel'))
    v_document.packages.append(pl.Package('fp'))
    v_document.packages.append(pl.Package('caption'))  # for figure captions outside a float environment

    # Packages to trim images
    v_document.packages.append(pl.Package('adjustbox'))

    # Packages to ensure floats stay inside section
    v_document.packages.append(pl.Package('placeins'))  # allows for \floatbarrier

    # Packages for coloring text
    v_document.packages.append(pl.Package('xcolor'))

    # Packages for TikZ
    v_document.packages.append(pl.Package('tikz'))

    #
    # Preamble
    #
    v_document.preamble.append(pl.NoEscape(r'\makeatletter'))
    v_document.preamble.append(pl.NoEscape(r'\newcommand{\personref}[2][I9999]{\@ifundefined{r@#1}{#2}{\hyperref[#1]{#2}$_{/\pageref{#1}/}$}}'))
    v_document.preamble.append(pl.NoEscape(r'\newcommand{\minspace}{5\baselineskip}'))

    # To get the integer part from a floating value
    v_document.preamble.append(pl.NoEscape(r'\newcommand{\intpart}[1]{\expandafter\int@part#1..\@nil}'))
    v_document.preamble.append(pl.NoEscape(r'\def\int@part#1.#2.#3\@nil{\if\relax#1\relax0\else#1\fi}'))
    v_document.preamble.append(pl.NoEscape(r'\makeatother'))

    # Only show levels up to Chapter in Table of Contents
    v_document.preamble.append(pl.NoEscape(r'\setcounter{tocdepth}{0}'))

    # Increase number width to prevent chapter numbers and heading titles from overlapping in the toc
    v_document.preamble.append(pl.NoEscape(r'\advance\cftchapnumwidth 1.0em\relax'))
    v_document.preamble.append(pl.NoEscape(r'\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}'))

    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height
    v_document.preamble.append(pl.NoEscape(r'\newsavebox\x'))
    v_document.preamble.append(pl.NoEscape(r'\newcount\widthImages'))
    v_document.preamble.append(pl.NoEscape(r'\newcount\widthAvailable'))

    # Counters for filling up wrapfigure in hkPersonChapter
    v_document.preamble.append(pl.NoEscape(r'\newcounter{maxlines}'))
    v_document.preamble.append(pl.NoEscape(r'\newcounter{mycounter}'))

    # Redefine labels fo chapters
    v_document.preamble.append(pl.NoEscape(r'\renewcommand{\contentsname}{' + hlg.translate('table of contents') + '}'))
    v_document.preamble.append(pl.NoEscape(r'\renewcommand{\listfigurename}{' + hlg.translate('list of figures') + '}'))
    v_document.preamble.append(pl.NoEscape(r'\renewcommand{\partname}{' + hlg.translate('generation') + '}'))
    v_document.preamble.append(pl.NoEscape(r'\renewcommand{\chaptername}{' + hlg.translate('chapter') + '}'))

    v_document.preamble.append(pl.Command('title', p_book_parameters['Title']))
    v_document.preamble.append(pl.Command('author', p_book_parameters['Author']))
    v_document.preamble.append(pl.Command('date', pu.NoEscape(r'\today')))

    # Define TikZ styles 20211227
    v_document.append(pu.NoEscape(r'\usetikzlibrary{arrows.meta, graphs}'))
    v_document.append(pu.NoEscape(r'\tikzset{thick, black!50, text=black}'))
    v_document.append(pu.NoEscape(r'\tikzset{>={Stealth[round]}}'))
    v_document.append(pu.NoEscape(r'\tikzset{graphs/every graph/.style={edges=rounded corners}}'))
    v_document.append(pu.NoEscape(r'\tikzset{point/.style={circle,inner sep=0pt,minimum size=5pt,fill=red}}'))
    v_document.append(pu.NoEscape(r'\tikzset{terminal/.style={circle,minimum size=6mm,very thick,draw=black!50,top color=white,bottom color=black!20,font=\ttfamily}}'))
    v_document.append(pu.NoEscape(r'\tikzset{date/.style={rectangle,rounded corners=3mm,minimum size=6mm,very thick,draw=green!50,top color=white,bottom color=green!50!black!20,font=\ttfamily}}'))
    v_document.append(pu.NoEscape(r'\tikzset{self/.style={thick,double}}'))
    v_document.append(pu.NoEscape(r'\tikzset{man/.style={rectangle,thick,draw=blue!50!black!50,top color=white, bottom color=blue!50!black!20,rounded corners=.8ex}}'))
    v_document.append(pu.NoEscape(r'\tikzset{woman/.style={rectangle,thick,draw=red!50!black!50,top color=white,bottom color=red!50!black!20,rounded corners=.8ex}}'))
    v_document.append(pu.NoEscape(r'\tikzset{left/.style={xshift=-2.5mm,anchor=east, minimum size=6mm}}'))
    v_document.append(pu.NoEscape(r'\tikzset{right/.style={xshift=2.5mm,anchor=west, minimum size=6mm}}'))
    v_document.append(pu.NoEscape(r'\tikzset{vh path/.style={to path={|- (\tikztotarget)}}}'))

    v_document.append(pu.NoEscape(r'\maketitle'))
    v_document.append(pl.Command('tableofcontents'))

    # Find handle of root person
    v_person_handle = hgd.get_person_handle_by_gramps_id(p_book_parameters['StartPersonId'], p_cursor)

    if v_person_handle is not None:
        # Write the Ahnentafel of this person
        v_ahnentafel = hac.Ahnentafel(v_person_handle, p_cursor, p_book_parameters['Path'], True)
        v_ahnentafel.create_ahnentafel_chapter()
        v_document.append(pl.NoEscape(r'\include{Ahnentafel}'))

        #
        # Build a book consisting of parts for each generation.
        # Each part will contain chapters for all persons in the Ahnentafel
        #
        v_multi_generation_list = v_ahnentafel.generation_list

        # Create sub list for first generation
        v_generation_index = 1
        v_generation_list = [x[0] for x in v_multi_generation_list if x[1] == v_generation_index]

        while len(v_generation_list) > 0:
            # Create a new part for this generation
            # v_part = hlt.Part(title=hlg.translate('generation') + ' ' + str(v_generation_index), label=False)
            v_part = hlt.Part(title=' ', label=False)
            v_part.generate_tex(filepath=p_book_parameters['Path'] + 'Part_' + str(v_generation_index))

            # Include the part to the document
            v_document.append(pl.NoEscape(r'\include{Part_' + str(v_generation_index) + '} % Generation ' + str(v_generation_index)))

            # Create a detailed chapter for each person in this generation
            for v_person_handle in v_generation_list:
                v_person = hpc.Person(v_person_handle, p_cursor, p_book_parameters['Path'], p_book_parameters['Language'])
                v_document.append(pl.NoEscape(r'\include{' + v_person.gramps_id + '} % ' + v_person.given_names + ' ' + v_person.surname))
                v_person.write_person_chapter()

            #  Create new sub list for next generation
            v_generation_index = v_generation_index + 1
            v_generation_list = [x[0] for x in v_multi_generation_list if x[1] == v_generation_index]

        #
        # OR
        # write a detailed chapter for each person by running iteratively through the family tree
        #
        # p_done_list = []
        # process_person(v_person_handle, p_cursor, v_document, p_document_path, p_done_list)

    v_document.generate_tex(filepath=p_book_parameters['Path'] + p_book_parameters['Filename'])

    # print("Number of persons processed: ", len(p_done_list))


def main():
    # Set logging level
    logging.basicConfig(filename='debug.log', format='%(module)s:%(funcName)s:%(levelname)s:%(message)s', level=logging.DEBUG)

    # ReadDatabase()
    v_book_parameters = read_config_xml()

    v_connection = sqlite3.connect('file:../db/sqlite.db?mode=ro', uri=True)
    v_cursor = v_connection.cursor()
    write_main_document(v_cursor, v_book_parameters)

    v_connection.close()


if __name__ == "__main__":
    main()
