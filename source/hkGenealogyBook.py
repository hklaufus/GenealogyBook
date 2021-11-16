import sqlite3
import os

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

def ReadConfigXml(pFileName = 'config.xml'):
    vBookParameters = {}
    vBookParameters['Author'] = '<Author>'
    vBookParameters['Title'] = '<Title>'
    vBookParameters['Filename'] = '<Filename>'
    vBookParameters['StartePersonId'] = 'I0000'
    vBookParameters['Language'] = 'nl'
    vBookParameters['Path'] = '../book/'

    # Filter is used only for children; parents will always be separately described
    vBookParameters['Filter'] = ['Surname1', 'Surname2']

    vDom = mdm.parse(pFileName)

    vBookParameters['Author'] = vDom.getElementsByTagName('Author')[0].childNodes[0].nodeValue
    vBookParameters['Title'] = vDom.getElementsByTagName('Title')[0].childNodes[0].nodeValue
    vBookParameters['Filename'] = vDom.getElementsByTagName('Filename')[0].childNodes[0].nodeValue
    vBookParameters['StartPersonId'] = vDom.getElementsByTagName('StartPersonId')[0].childNodes[0].nodeValue
    vBookParameters['Language'] = vDom.getElementsByTagName('Language')[0].childNodes[0].nodeValue
    vBookParameters['Path'] = vDom.getElementsByTagName('Path')[0].childNodes[0].nodeValue

    #Debug
#    print("vBookParameters: ", vBookParameters)

    return vBookParameters

def ProcessPerson(pPersonHandle, pCursor, pDocument, pDocumentPath, vDoneList):
    if (pPersonHandle not in vDoneList):
        # Add person to Done list to prevent of processing twice
        vDoneList.append(pPersonHandle)

        vPerson = hpc.Person(pPersonHandle, pCursor)

        if (vPerson.GrampsId is not None):
            # Fetch parents + children
            vProcessList = []
            vProcessList.append(vPerson.FatherHandle)
            vProcessList.append(vPerson.MotherHandle)

            if(len(vFilter) > 0):
                # Only persons with relation to vStartPersonId and surnames as
                # per filter
                for vChildHandle in vPerson.ChildrenHandlesList:
                    vChild = hpc.Person(vChildHandle, pCursor)
                    if(vChild.Surname in vFilter):
                        vProcessList.append(vChild.PersonHandle)
            else:
                # Anyone in database with relation to vStartPersonId
                vProcessList = vProcessList + vPerson.ChildrenHandlesList

            # Create chapter in sub-document describing current person
            pDocument.append(pl.NoEscape(r'\include{' + vPerson.GrampsId + '} % ' + vPerson.GivenNames + ' ' + vPerson.Surname))
            vPerson.WritePersonChapter()

            # Process stack
            for vNextPerson in vProcessList:
                if (vNextPerson is not None):
                    ProcessPerson(vNextPerson, pCursor, pDocument, pDocumentPath, vDoneList)
        #                else:
        #                    print('ERROR fetching vNextPerson')
        #                    print("vNextPerson: ", vNextPerson)
        else:
            print('ERROR fetching vPerson.GrampsId')
            print("vPerson.GrampsId: ", vPerson.GrampsId)


def WriteMainDocument(pCursor, pBookParameters):
    # vGeometryOptions = {"tmargin": "1cm", "lmargin": "10cm"}
    vDocumentOptions = {'hidelinks', '10pt', 'a4paper', 'titlepage'}
    vDocument = pl.Document(documentclass='book', document_options=vDocumentOptions)

    #
    # Packages
    #

    # vDocument.packages.append(pl.Package('lipsum'))
    vDocument.packages.append(pl.Package('blindtext'))
    vDocument.packages.append(pl.Package('hyperref'))
    vDocument.packages.append(pl.Package('graphicx'))

    # https://tex.stackexchange.com/questions/118602/how-to-text-wrap-an-image-in-latex#132313
    vDocument.packages.append(pl.Package('wrapfig'))
    vDocument.packages.append(pl.Package('tocloft'))
    vDocument.packages.append(pl.Package('needspace'))

    # The next packages should be automatically inserted by PyLaTeX??
    vDocument.packages.append(pl.Package('tabu'))
    vDocument.packages.append(pl.Package('longtable'))

    # Packages to scale images
    vDocument.packages.append(pl.Package('scalerel'))
    vDocument.packages.append(pl.Package('fp'))
    vDocument.packages.append(pl.Package('caption'))

    # Packages to ensure floats stay inside section
    vDocument.packages.append(pl.Package('placeins'))

    #
    # Preamble
    #
    vDocument.preamble.append(pl.NoEscape(r'\makeatletter'))
    vDocument.preamble.append(pl.NoEscape(r'\newcommand{\personref}[2][I9999]{\@ifundefined{r@#1}{#2}{\hyperref[#1]{#2}$_{/\pageref{#1}/}$}}'))
    vDocument.preamble.append( pl.NoEscape(r'\newcommand{\minspace}{5\baselineskip}'))
    vDocument.preamble.append(pl.NoEscape(r'\makeatother'))

    # Only show levels up to Chapter in Table of Contents
    vDocument.preamble.append(pl.NoEscape(r'\setcounter{tocdepth}{0}'))

    # Increase number width to prevent chapter numbers and heading titles from overlapping in the toc
    vDocument.preamble.append( pl.NoEscape(r'\advance\cftchapnumwidth 1.0em\relax'))
    vDocument.preamble.append( pl.NoEscape(r'\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}'))

    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height
    vDocument.preamble.append(pl.NoEscape(r'\newsavebox\x'))
    vDocument.preamble.append(pl.NoEscape(r'\newcount\imgwidthA'))
    vDocument.preamble.append(pl.NoEscape(r'\newcount\textwidthA'))

    # Redefine labels fo chapters
    vDocument.preamble.append(pl.NoEscape(r'\renewcommand{\contentsname}{' + hlg.Translate('table of contents') + '}'))
    vDocument.preamble.append(pl.NoEscape(r'\renewcommand{\listfigurename}{' + hlg.Translate('list of figures') + '}'))
    vDocument.preamble.append(pl.NoEscape(r'\renewcommand{\partname}{' + hlg.Translate('generation') + '}'))
    vDocument.preamble.append(pl.NoEscape(r'\renewcommand{\chaptername}{' + hlg.Translate('chapter') + '}'))

    vDocument.preamble.append(pl.Command('title', pBookParameters['Title']))
    vDocument.preamble.append(pl.Command('author', pBookParameters['Author']))
    vDocument.preamble.append(pl.Command('date', pu.NoEscape(r'\today')))

    vDocument.append(pu.NoEscape(r'\maketitle'))
    vDocument.append(pl.Command('tableofcontents'))

    # Find handle of root person
    vPersonHandle = hgd.GetPersonHandleByGrampsId(pBookParameters['StartPersonId'], pCursor)

    if (vPersonHandle is not None):
        # Write the Ahnentafel of this person
        vAhnentafel = hac.Ahnentafel(vPersonHandle, pCursor, pBookParameters['Path'], True)
        vAhnentafel.CreateAhnentafelChapter()
        vDocument.append(pl.NoEscape(r'\include{Ahnentafel}'))

        #
        # Build a book consiting of parts for each generation.
        # Each part will contain chapters for all persons in the Ahnentafel
        #
        vMultiGenerationList = vAhnentafel.GenerationList

        # Create sub list for first generation
        vGenerationIndex = 1
        vGenerationList = [x[0] for x in vMultiGenerationList if x[1] == vGenerationIndex]

        while (len(vGenerationList) > 0):
            # Create a new part for this generation
            vPart = hlt.Part(title=hlg.Translate('generation') + ' ' + str(vGenerationIndex), label=False)
            vPart = hlt.Part(title=' ', label=False)
            vPart.generate_tex(filepath=pBookParameters['Path'] + 'Part_' + str(vGenerationIndex))

            # Include the part to the document
            vDocument.append(pl.NoEscape(r'\include{Part_' + str(vGenerationIndex) + '} % Generation ' + str(vGenerationIndex)))

            # Create a detailed chapter for each person in this generation
            for vPersonHandle in vGenerationList:
                vPerson = hpc.Person(vPersonHandle, pCursor, pBookParameters['Path'], pBookParameters['Language'])
                vDocument.append(pl.NoEscape(r'\include{' + vPerson.GrampsId + '} % ' + vPerson.GivenNames + ' ' + vPerson.Surname))
                vPerson.WritePersonChapter()

            #  Create new sub list for next generation
            vGenerationIndex = vGenerationIndex + 1
            vGenerationList = [x[0] for x in vMultiGenerationList if x[1] == vGenerationIndex]

        #
        # OR
        # write a detailed chapter for each person by running iteratively through the family tree
        #
#		vDoneList = []
#		ProcessPerson(vPersonHandle, pCursor, vDocument, pDocumentPath, vDoneList)

    vDocument.generate_tex(filepath=pBookParameters['Path'] + pBookParameters['Filename'])

#	print("Number of persons processed: ", len(vDoneList))


def Main():
    # ReadDatabase()
    vBookParameters = ReadConfigXml()

    vConnection = sqlite3.connect('file:../db/sqlite.db?mode=ro', uri=True)
    vCursor = vConnection.cursor()
    WriteMainDocument(vCursor, vBookParameters)

    vConnection.close()
