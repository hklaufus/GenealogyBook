import hkLanguage as hlg
import hkPersonChapter as hpc
import hkGrampsDb as hgd
import hkLatex as hlt

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc


class Ahnentafel:
    """A class to write a ahnentafel chapter"""

    def __init__(self, pSubjectHandle, pCursor, pDocumentPath='../book/', pSourceStatus=False):
        self.__PersonHandle = pSubjectHandle
        self.__Cursor = pCursor
        self.__DocumentPath = pDocumentPath

        # Adds the status of sources to the Ahnentafel
        self.__SourceStatus = pSourceStatus

        #  Create a generation list
        self.__GenerationList = []
        self.__CreateGenerationList(self.__PersonHandle, 1)

    @property
    def GenerationList(self):
        return self.__GenerationList

    def __AddPerson(self, pPersonHandle, pBinaryTreeString):
        vPerson = hpc.Person(pPersonHandle, self.__Cursor, self.__DocumentPath)

        # Display progress
        print("Adding: ", vPerson.GivenNames, vPerson.Surname)

        vPreString = ''
        for vIndex in range(1, len(pBinaryTreeString)):
            vPreString = vPreString + r'\quad\quad'

        vString = vPreString + ' ' + pBinaryTreeString + r'\quad\quad ' + pu.escape_latex(vPerson.GivenNames) + ' ' + pu.escape_latex(vPerson.Surname) + r'\newline'
        print(vString)

        self.__Chapter.append(pl.NoEscape(vString))

        vFatherHandle = vPerson.FatherHandle
        if(vFatherHandle is not None):
            self.__AddPerson(vFatherHandle, pBinaryTreeString + 'M')
        else:
            print("End of tree...")

        vMotherHandle = vPerson.MotherHandle
        if(vMotherHandle is not None):
            self.__AddPerson(vMotherHandle, pBinaryTreeString + 'F')
        else:
            print("End of tree...")

    def __AddGeneration(self, pGenerationList):
        """
        The Generation list consists of tuples (person_handle, binary_tree_string)
        """
        vGenerationIndex = len(pGenerationList[0][1]) + 1  # The generation index is determined using the length of the binary string
        vNextGenerationList = []
        vSection = None

        if(len(pGenerationList) > 0):
            vGenerationStarted = False
            for (vPersonHandle, vBinaryTreeString) in pGenerationList:
                if (vPersonHandle is not None):
                    if(not vGenerationStarted):
                        with self.__Chapter.create(pl.Section(numbering=False, title=hlg.Translate('generation') + ' ' + str(vGenerationIndex), label=False)):
                            vGenerationStarted = True
                            if(self.__SourceStatus):
                                self.__Chapter.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth} | c | c | c |}%'))
                            else:
                                self.__Chapter.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth}}%'))

                    vPerson = hpc.Person(vPersonHandle, self.__Cursor, self.__DocumentPath)
                    vSourceStatus = vPerson.SourceStatus

                    vNewBinaryString = ''
                    if(vGenerationIndex == 1):
                        vNewBinaryString = 'X'
                    elif(vPerson.Gender == 0):
                        vNewBinaryString = vBinaryTreeString + 'F'
                    elif(vPerson.Gender == 1):
                        vNewBinaryString = vBinaryTreeString + 'M'
                    else:
                        vNewBinaryString = vBinaryTreeString + '_'

                    if(self.__SourceStatus):
                        # Research help: Add the source status to the
                        # Ahnentafel
                        self.__Chapter.append(pl.NoEscape(hlt.GetPersonNameWithReference(vPerson.GivenNames, vPerson.Surname, vPerson.GrampsId) + r' & ' + vNewBinaryString + r' & ' + vSourceStatus['b'] + r' & ' + vSourceStatus['m'] + r' & ' + vSourceStatus['d'] + r'\\'))
                    else:
                        self.__Chapter.append(pl.NoEscape(hlt.GetPersonNameWithReference(vPerson.GivenNames, vPerson.Surname, vPerson.GrampsId) + r' & ' + vNewBinaryString + r'\\'))

                    vNextGenerationList.append((vPerson.FatherHandle, vNewBinaryString))
                    vNextGenerationList.append((vPerson.MotherHandle, vNewBinaryString))

            if(vGenerationStarted):
                self.__Chapter.append(pl.NoEscape(r'\end{longtabu}%'))
                vGenerationStarted = False

        if(len(vNextGenerationList) > 0):
            self.__AddGeneration(vNextGenerationList)

    def __CreateGenerationList(self, pPersonHandle, pGenerationIndex):
        if (pPersonHandle is not None):
            vPerson = hpc.Person(pPersonHandle, self.__Cursor, self.__DocumentPath)

            # Add this person to the objects generation list
            self.__GenerationList.append((pPersonHandle, pGenerationIndex))

            # Add siblings to the objects generation list
            vSiblingHandleList = hgd.GetSiblingHandles_Old(pPersonHandle, self.__Cursor)
            for vSiblingHandle in vSiblingHandleList:
                if (vSiblingHandle is not None):
                    self.__GenerationList.append(
                        (vSiblingHandle, pGenerationIndex))

            # Process the parents
            self.__CreateGenerationList(vPerson.FatherHandle, pGenerationIndex + 1)
            self.__CreateGenerationList(vPerson.MotherHandle, pGenerationIndex + 1)

    def CreateAhnentafelChapter(self):
        """
        Writes the ahnentafel to a separate chapter in a subdocument
        """

        vSubject = hpc.Person(self.__PersonHandle, self.__Cursor, self.__DocumentPath)

        # Display progress
        print("Writing the Ahnentafel...")

        # Create a new chapter for the active person
        self.__Chapter = hlt.Chapter(title=hlg.Translate('pedigree of') + ' ' + vSubject.GivenNames + ' ' + vSubject.Surname, label=False)
#		self.__AddPerson(self.__PersonHandle, 'X')
        self.__AddGeneration([(self.__PersonHandle, '')])
        self.__Chapter.generate_tex(filepath=self.__DocumentPath + 'Ahnentafel')
