# Formatted using "python3-autopep8 --in-place --aggressive --aggressive *.py"

import hkLanguage as hlg
#import hkGrampsDb as hgd
import hkLatex as hlt

from hkGrampsDb import *

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc

from PIL import Image
# Prevents PIL.Image.DecompressionBombError: Image size (... pixels)
# exceeds limit of .... pixels, could be decompression bomb DOS attack.
Image.MAX_IMAGE_PIXELS = None


# Constants
cPublishable = 'Publishable'
cDocument = 'Document'
cPhoto = 'Photo'
cSource = 'Source'


class Person:
    """A class to write a chapter about a person"""

    @property
    def PersonHandle(self):
        return self.__PersonHandle

    @property
    def DocumentPath(self):
        return self.__DocumentPath

    @property
    def GrampsId(self):
        return self.__GrampsId

    @property
    def Gender(self):
        return self.__Gender

    @property
    def GivenNames(self):
        return self.__GivenNames

    @property
    def Surname(self):
        return self.__Surname

    @property
    def FatherHandle(self):
        return self.__FatherHandle

    @property
    def MotherHandle(self):
        return self.__MotherHandle

    @property
    def ChildrenHandlesList(self):
        return self.__ChildrenHandlesList

    @property
    def SourceStatus(self):
        return self.__SourceStatus

    def __init__(self, pPersonHandle, pCursor, pDocumentPath='../book/', pLanguage='nl'):
        self.__PersonHandle = pPersonHandle
        self.__Cursor = pCursor
        self.__DocumentPath = pDocumentPath
        self.__language = pLanguage

        # Get basic person data
        vPersonData = DecodePersonData(self.__PersonHandle, self.__Cursor)
        self.__GrampsId = vPersonData[1]
        self.__Gender = vPersonData[2]
        self.__Surname = vPersonData[3][0]
        self.__GivenNames = vPersonData[3][1]
        self.__CallName = vPersonData[3][2]
        self.__EventRefList = vPersonData[7]
        self.__FamilyList = vPersonData[8]
        self.__ParentFamilyList = vPersonData[9]
        self.__MediaList = vPersonData[10]

        self.__NoteBase = vPersonData[16]
#		self.__NotesHandlesList = GetPersonNotesHandles(self.__PersonHandle, self.__Cursor)

        self.__PartnerHandleList = GetPartnerHandles(self.__PersonHandle, self.__Cursor)
        self.__ChildrenHandlesList = GetChildrenHandlesByPerson(self.__PersonHandle, self.__Cursor)

        self.__FatherHandle = GetFatherHandleByPerson(self.__PersonHandle, self.__Cursor)
        self.__MotherHandle = GetMotherHandleByPerson(self.__PersonHandle, self.__Cursor)
        self.__SiblingHandlesList = GetSiblingHandles_Old(self.__PersonHandle, self.__Cursor)

        self.__CreateEventDictionary()

        # TODO: This is a tag list NOT related to one person; this does not belong here
        self.__TagDictionary = GetTagDictionary(self.__Cursor)

        self.__SourceStatus = self.__GetSourceStatus()

    def __CreateEventDictionary(self):
        # Create an event dictionary.
        # The key refers to the type of event (eg. Profession); the value contains a list of events belonging to this event type (eg. multiple professions within key Profession)
        # Key:[event info, event info 2, event info 3]
        self.__PersonEventInfoDict = {}
        for vEventRef in self.__EventRefList:
            vEventHandle = vEventRef[3]
            vEventInfo = DecodeEventData(vEventHandle, self.__Cursor)
            
            # Filter on role
            vRoleType = vEventRef[4][0]
            if(vRoleType == vRolePrimary) or (vRoleType == vRoleFamily):
                # Create a dictionary from event data. Use event type as key, and rest of event as data

                # Check whether event type already exists as key
                if(vEventInfo[0] in self.__PersonEventInfoDict):
                    # if so, append event info to the dictionary entry
                    self.__PersonEventInfoDict[vEventInfo[0]].append(vEventInfo[1:])
                else:
                    # Otherwise create a new entry
                    self.__PersonEventInfoDict[vEventInfo[0]] = [vEventInfo[1:]]

                # Add event media to personal media list
                self.__MediaList = self.__MediaList + vEventInfo[4]

    def __GetSourceStatus(self):
        """ Checks whether scans ar avaiable for the events birth, marriage and death """

        vSourceStatus = {'b': '', 'm': '', 'd': ''}  # birth, marriage, death

        # Birth / baptism
        vMediaList = []
        if(vEventBirth in self.__PersonEventInfoDict):  # Birth
            vEventInfo = self.__PersonEventInfoDict[vEventBirth]
            vMediaList.extend(vEventInfo[0][3])

        if(vEventBaptism in self.__PersonEventInfoDict):  # Baptism
            vEventInfo = self.__PersonEventInfoDict[vEventBaptism]
            vMediaList.extend(vEventInfo[0][3])

        if(len(vMediaList) > 0):
            vSourceStatus['b'] = 'b'

        # Marriage
        vMediaList = []
        for vFamilyHandle in self.__FamilyList:
            vFamilyInfo = DecodeFamilyData(vFamilyHandle, self.__Cursor)
            vEventRefList = vFamilyInfo[5]

            for vEvent in vEventRefList:
                vEventHandle = vEvent[3]
                vEventInfo = DecodeEventData(vEventHandle, self.__Cursor)
                vType = vEventInfo[0]
                vMediaList = vEventInfo[4]

                # 1 = Marriage, 2 = Marriage Settlement, 3 = Marriage License,
                # 4 = Marriage Contract
                if((vType == vEventMarriage or vType == vEventMarriageSettlement or vType == vEventMarriageLicense or vType == vEventMarriageContract) and (len(vMediaList) > 0)):
                    vSourceStatus['m'] = 'm'

        # Death / Burial
        vMediaList = []
        if(vEventDeath in self.__PersonEventInfoDict):  # Death
            vEventInfo = self.__PersonEventInfoDict[vEventDeath]
            vMediaList.extend(vEventInfo[0][3])

        if(vEventBurial in self.__PersonEventInfoDict):  # Burial
            vEventInfo = self.__PersonEventInfoDict[vEventBurial]
            vMediaList.extend(vEventInfo[0][3])

        if(len(vMediaList) > 0):
            vSourceStatus['d'] = 'd'

        return vSourceStatus

    def __GetFilteredPhotoList(self):
        vPhotoList = []

        for vMediaItem in self.__MediaList:
            vMediaHandle = vMediaItem[4]
            vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
            vMediaMime = vMediaData[3]
            vTagHandleList = vMediaData[11]

            if((vMediaMime.lower() == 'image/jpeg') or (vMediaMime.lower() == 'image/png')):
                if (cPublishable in GetTagList(vTagHandleList, self.__TagDictionary)) and (cPhoto in GetTagList(vTagHandleList, self.__TagDictionary)):
                    vPhotoList.append(vMediaHandle)

        return vPhotoList

    def __GetFilteredDocumentList(self):
        vDocumentList = []

        for vMediaItem in self.__MediaList:
            vMediaHandle = vMediaItem[4]
            vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
            vMediaMime = vMediaData[3]
            vTagHandleList = vMediaData[11]

            if((vMediaMime.lower() == 'image/jpeg') or (vMediaMime.lower() == 'image/png')):
                if (cPublishable in GetTagList(vTagHandleList, self.__TagDictionary)) and (cDocument in GetTagList(vTagHandleList, self.__TagDictionary)):
                    vDocumentList.append(vMediaHandle)

        return vDocumentList

    def __GetFilteredNoteList(self, pNoteHandleList):
        """
        Removes all notes from pNoteHandleList that are of type 'Citation' or that are tagged 'Source'
        """

        vNoteList = []

        for vNoteHandle in pNoteHandleList:
            vNoteData = DecodeNoteData(vNoteHandle, self.__Cursor)
            vTagHandleList = vNoteData[6]
            vType = vNoteData[4][0]

            if not (cSource in GetTagList(vTagHandleList, self.__TagDictionary)) and not (vType == vNoteCitation):
                vNoteList.append(vNoteHandle)

        return vNoteList

    def __PictureSideBySideEqualHeight(self, pImageData_1, pImageData_2):
        # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

        self.__Chapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[scale=0.1]{"' + pImageData_1[2] + r'"}}'))  # Added scale to prevent overflow in scalerel package
        self.__Chapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + pImageData_2[2] + r'"}}'))
        self.__Chapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))
        self.__Chapter.append(pl.NoEscape(r'\imgwidthA=\wd\x'))
        self.__Chapter.append(pl.NoEscape(r'\textwidthA=\dimexpr\textwidth-5ex'))
        self.__Chapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\textwidthA}{\the\imgwidthA}'))
        self.__Chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))
        self.__Chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
        self.__Chapter.append(pl.NoEscape(r'\box0'))
        self.__Chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageData_1[4]) + '}'))
        self.__Chapter.append(pl.NoEscape(r'\end{minipage}\kern3ex'))
        self.__Chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
        self.__Chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
        self.__Chapter.append(pl.NoEscape(r'\box0'))
        self.__Chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageData_2[4]) + '}'))
        self.__Chapter.append(pl.NoEscape(r'\end{minipage}'))
        self.__Chapter.append(pl.NoEscape(r'\newline\newline'))

    def __PictureWithNote(self, pImageData):
        self.__DocumentWithNote(pImageData)

    def __DocumentWithNote(self, pImageData):
        # Check on portait vs landscape
        vImage = Image.open(pImageData[2], mode='r')
        vWidth, vHeight = vImage.size

        self.__Chapter.append(pl.NoEscape(r'\subsubsection*{}'))
        if(vWidth > vHeight):
            # Landscape
            self.__Chapter.append(pl.NoEscape(r'{'))
            self.__Chapter.append(pl.NoEscape(r'\centering'))
            self.__Chapter.append(pl.NoEscape(r'\includegraphics[width=0.95\textwidth]{"' + pImageData[2] + r'"}'))
            self.__Chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex( pImageData[4]) + r'}'))
            self.__Chapter.append(pl.NoEscape(r'}'))
            self.__Chapter.append(pl.NoEscape(r'\vspace{1ex}'))
        else:
            # Portrait
            self.__Chapter.append(pl.NoEscape(r'\begin{wrapfigure}{r}{0.50\textwidth}'))
            self.__Chapter.append(pl.NoEscape(r'\centering'))
            self.__Chapter.append(pl.NoEscape(r'\includegraphics[width=0.45\textwidth]{"' + pImageData[2] + r'"}'))
            self.__Chapter.append(pl.NoEscape(r'\caption{' + pu.escape_latex(pImageData[4]) + r'}'))
            self.__Chapter.append(pl.NoEscape(r'\end{wrapfigure}'))

        # Add note(s)
        vNoteBase = pImageData[8]
#		self.__Chapter.append(pl.NoEscape(r'\subsubsection*{}'))
#		self.__Chapter.append(pl.NoEscape(r'\begin{flushleft}'))
        for vNoteHandle in vNoteBase:
            vNoteData = DecodeNoteData(vNoteHandle, self.__Cursor)
            vNoteText = vNoteData[2][0]
            vTagHandleList = vNoteData[6]
            self.__Chapter.append(pl.NoEscape(pu.escape_latex(vNoteText)))
#			self.__Chapter.append(pl.NoEscape(r'\newline\newline'))
            self.__Chapter.append(pl.NoEscape(r'\par'))
#		self.__Chapter.append(pl.NoEscape(r'\end{flushleft}'))


    def __WriteLifeSketchSection(self):
        # Create section with Life Sketch
        self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
        with self.__Chapter.create(pl.Section(title=hlg.Translate('life sketch', self.__language), label=False)):
            # Create a minipage for a picture
            for vMediaItem in self.__MediaList:
                vMediaHandle = vMediaItem[4]
                vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                vMediaPath = vMediaData[2]
                vMediaMime = vMediaData[3]
                vMediaDescription = vMediaData[4]
                vTagHandleList = vMediaData[11]

                if ('Portrait' in GetTagList(vTagHandleList, self.__TagDictionary)):
                    self.__Chapter.append(pl.NoEscape(r'\begin{wrapfigure}{r}{0.40\textwidth}'))
                    self.__Chapter.append(pl.NoEscape(r'\centering'))
                    self.__Chapter.append(pl.NoEscape(r'\includegraphics[width=0.38\textwidth]{"' + vMediaPath + r'"}'))
#					self.__Chapter.append(pl.NoEscape(r'\caption{'+pu.escape_latex(vMediaDescription)+r'}'))
                    self.__Chapter.append(pl.NoEscape(r'\end{wrapfigure}'))

            # Create a story line
            vLifeSketch = ""

            for vNote in self.__NoteBase:
                vNoteHandle = vNote
                vNoteData = DecodeNoteData(vNoteHandle, self.__Cursor)
                vNoteText = vNoteData[2][0]
                vNoteType = vNoteData[4][0]
                if(vNoteType == vNotePerson):  # Person Note
                    vLifeSketch = vLifeSketch + pu.escape_latex(vNoteText)

            if(len(vLifeSketch) == 0):
                vFullName = self.__GivenNames + ' ' + self.__Surname
                vHeShe = hlg.Translate('He', self.__language)
                vHisHer = hlg.Translate('His', self.__language)
                if(self.__Gender == vGenderFemale):
                    vHeShe = hlg.Translate('She', self.__language)
                    vHisHer = hlg.Translate('Her', self.__language)

                vVitalEvents = vVitalEventsSet.intersection(self.__PersonEventInfoDict.keys())

                # Geboorte
                if(vEventBirth in vVitalEvents):  # Birth
                    vString = hlg.Translate("{0} was born on {1}", self.__language).format(pu.escape_latex(vFullName), DateToText(self.__PersonEventInfoDict[vEventBirth][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBirth][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBirth][0][1] != '-')):
                        vString = hlg.Translate("in {0}", self.__language).format(self.__PersonEventInfoDict[vEventBirth][0][1])
                        vLifeSketch = vLifeSketch + ' ' + vString

                    vLifeSketch = vLifeSketch + r". "

                elif(vEventBaptism in vVitalEvents):  # Baptism
                    vString = hlg.Translate("{0} was born about {1}", self.__language).format(pu.escape_latex(vFullName), DateToText(self.__PersonEventInfoDict[vEventBaptism][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBaptism][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBaptism][0][1] != '-')):
                        vString = hlg.Translate("in {0}", self.__language).format(self.__PersonEventInfoDict[vEventBaptism][0][1])
                        vLifeSketch = vLifeSketch + ' ' + vString

                    vLifeSketch = vLifeSketch + r". "

                # Roepnaam
                vUseName = self.__GivenNames
                if(len(self.__CallName) > 0):
                    vUseName = self.__CallName
                    vString = hlg.Translate("{0} call name was {1}.", self.__language).format(vHisHer, pu.escape_latex(self.__CallName))
                    vLifeSketch = vLifeSketch + vString

                if(len(vLifeSketch) > 0):
                    vLifeSketch = vLifeSketch + r"\newline\newline "

                # Sisters and brothers
                vNumberSisters = 0
                vNumberBrothers = 0
                vSiblingNames = []
                vHasSiblings = False
                for vSiblingHandle in self.__SiblingHandlesList:
                    # TODO: Sort by birth date
                    vSiblingData = DecodePersonData(vSiblingHandle, self.__Cursor)
                    if(vSiblingData[2] == 0):
                        vNumberSisters = vNumberSisters + 1
                        vHasSiblings = True
                    elif(vSiblingData[2] == 1):
                        vNumberBrothers = vNumberBrothers + 1
                        vHasSiblings = True

                    vSiblingNames.append(vSiblingData[3][1])

                if(vNumberSisters > 0):
                    if(vNumberSisters == 1):
                        vString = hlg.Translate("{0} had one sister", self.__language).format(vUseName)
                        vLifeSketch = vLifeSketch + vString
                    else:
                        vString = hlg.Translate("{0} had {1} sisters", self.__language).format(vUseName, vNumberSisters)
                        vLifeSketch = vLifeSketch + vString

                    if(vNumberBrothers > 0):
                        if(vNumberBrothers == 1):
                            vLifeSketch = vLifeSketch + ' ' + hlg.Translate("and one brother:", self.__language) + ' '
                        else:
                            vString = hlg.Translate("and {0} brothers:", self.__language).format(vNumberBrothers)
                            vLifeSketch = vLifeSketch + ' ' + vString + ' '
                    else:
                        vLifeSketch = vLifeSketch + ": "

                elif(vNumberBrothers > 0):
                    if(vNumberBrothers == 1):
                        vString = hlg.Translate("{0} had one brother:", self.__language).format(vUseName)
                        vLifeSketch = vLifeSketch + vString + ' '
                    else:
                        vString = hlg.Translate("{0} had {1} brothers:", self.__language).format(vUseName, vNumberBrothers)
                        vLifeSketch = vLifeSketch + vString + ' '

                if(len(vSiblingNames) > 1):
                    for vSiblingName in vSiblingNames[:-1]:
                        vLifeSketch = vLifeSketch + pu.escape_latex(vSiblingName) + ", "

                    vLifeSketch = vLifeSketch + hlg.Translate("and", self.__language) + ' ' + pu.escape_latex(vSiblingNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\newline\newline "
                elif(len(vSiblingNames) == 1):
                    vLifeSketch = vLifeSketch + pu.escape_latex(vSiblingNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\newline\newline "

                # Partners and Children
                vNumberDaughters = 0
                vNumberSons = 0
                vChildNames = []
                for vChildHandle in self.__ChildrenHandlesList:
                    vChildData = DecodePersonData(vChildHandle, self.__Cursor)
                    if(vChildData[2] == 0):
                        vNumberDaughters = vNumberDaughters + 1
                    elif(vChildData[2] == 1):
                        vNumberSons = vNumberSons + 1

                    vChildNames.append(vChildData[3][1])

                vSentenceStart = hlg.Translate("Furthermore, {0} had", self.__language).format(vHeShe.lower()) + ' '
                if(len(vLifeSketch) == 0):
                    vSentenceStart = vFullName + hlg.Translate("had", self.__language) + ' '

                if(vNumberDaughters > 0):
                    vLifeSketch = vLifeSketch + vSentenceStart
                    if(vNumberDaughters == 1):
                        vLifeSketch = vLifeSketch + hlg.Translate("one daughter", self.__language)
                    elif(vNumberDaughters > 1):
                        vString = hlg.Translate("{0} daughters", self.__language).format(vNumberDaughters)
                        vLifeSketch = vLifeSketch + vString

                    if(vNumberSons > 0):
                        if(vNumberSons == 1):
                            vLifeSketch = vLifeSketch + ' ' + hlg.Translate("and one son:", self.__language) + ' '
                        else:
                            vString = hlg.Translate("and {0} sons:", self.__language).format(vNumberSons)
                            vLifeSketch = vLifeSketch + ' ' + vString + ' '
                    else:
                        vLifeSketch = vLifeSketch + ": "

                elif(vNumberSons > 0):
                    vLifeSketch = vLifeSketch + vSentenceStart
                    if(vNumberSons == 1):
                        vLifeSketch = vLifeSketch + \
                            hlg.Translate("one son:", self.__language) + ' '
                    else:
                        vString = hlg.Translate("{0} sons:", self.__language).format(vNumberSons)
                        vLifeSketch = vLifeSketch + vString + ' '

                if(len(vChildNames) > 1):
                    for vChildName in vChildNames[:-1]:
                        vLifeSketch = vLifeSketch + \
                            pu.escape_latex(vChildName) + ", "

                    vLifeSketch = vLifeSketch + hlg.Translate("and", self.__language) + ' ' + pu.escape_latex(vChildNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\newline\newline "
                elif(len(vChildNames) == 1):
                    vLifeSketch = vLifeSketch + \
                        pu.escape_latex(vChildNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\newline\newline "


#				if(len(vLifeSketch)>0):
#					vLifeSketch = vLifeSketch + r"\newline "

                # Overlijden
                if(vEventDeath in vVitalEvents):  # Death
                    vString = hlg.Translate("{0} died on {1}", self.__language).format(vHeShe, DateToText(self.__PersonEventInfoDict[vEventDeath][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventDeath][0][1]) > 0) and (self.__PersonEventInfoDict[vEventDeath][0][1] != '-')):
                        vString = hlg.Translate("in {0}.", self.__language).format(self.__PersonEventInfoDict[vEventDeath][0][1])
                        vLifeSketch = vLifeSketch + ' ' + vString
                    else:
                        vLifeSketch = vLifeSketch + ". "

                elif(vEventBurial in vVitalEvents):  # Burial
                    vString = hlg.Translate("{0} died about {1}", self.__language).format(vHeShe, DateToText(self.__PersonEventInfoDict[vEventBurial][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBurial][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBurial][0][1] != '-')):
                        vString = hlg.Translate("and was buried in {0}.", self.__language).format(self.__PersonEventInfoDict[vEventBurial][0][1])
                        vLifeSketch = vLifeSketch + ' ' + vString + ' '
                    else:
                        vLifeSketch = vLifeSketch + ". "

            self.__Chapter.append(pl.NoEscape(vLifeSketch))
            self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteVitalInformationSection(self):
        # Create section with Vital Information
        self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
        with self.__Chapter.create(pl.Section(title=hlg.Translate('vital information', self.__language), label=False)):
            with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                if(len(self.__CallName) > 0):
                    vTable.add_row([hlg.Translate('call name', self.__language) + ":", self.__CallName])

                if(self.__Gender in vGenderDict):
                    vTable.add_row([hlg.Translate('gender', self.__language) + ":", hlg.Translate(vGenderDict[self.__Gender], self.__language)])

                for vEvent in self.__PersonEventInfoDict.keys():
                    if (vEvent in vVitalEventsSet):
                        vString_1 = "Date of " + vEventTypeDict[vEvent]
                        vString_2 = "Place of " + vEventTypeDict[vEvent]

                        vTable.add_row([hlg.Translate(vString_1, self.__language) + ":", DateToText(self.__PersonEventInfoDict[vEvent][0][0], False)])
                        vTable.add_row([hlg.Translate(vString_2, self.__language) + ":", self.__PersonEventInfoDict[vEvent][0][1]])

            self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteParentalSubsection(self):
        # Add Family table
        self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
        with self.__Chapter.create(pl.Subsection(title=hlg.Translate('parental family', self.__language), label=False)):
            with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                vFatherName = 'Unknown'
                if(self.__FatherHandle is not None):
                    vFatherData = DecodePersonData(self.__FatherHandle, self.__Cursor)
                    vFatherName = pl.NoEscape(hlt.GetPersonNameWithReference(vFatherData[3][1], vFatherData[3][0], vFatherData[1]))

                vTable.add_row([hlg.Translate('father', self.__language) + ":", vFatherName])

                vMotherName = 'Unknown'
                if(self.__MotherHandle is not None):
                    vMotherData = DecodePersonData(self.__MotherHandle, self.__Cursor)
                    vMotherName = pl.NoEscape(hlt.GetPersonNameWithReference(vMotherData[3][1], vMotherData[3][0], vMotherData[1]))

                vTable.add_row([hlg.Translate('mother', self.__language) + ":", vMotherName])

                for vSiblingHandle in self.__SiblingHandlesList:
                    vSiblingData = DecodePersonData(vSiblingHandle, self.__Cursor)
                    if(vSiblingData[1] == self.__GrampsId):
                        vSiblingType = hlg.Translate('self', self.__language) + ":"
                    elif(vSiblingData[2] == 0):
                        vSiblingType = hlg.Translate('sister', self.__language) + ":"
                    elif(vSiblingData[2] == 1):
                        vSiblingType = hlg.Translate('brother', self.__language) + ":"
                    else:
                        vSiblingType = hlg.Translate('unknown', self.__language) + ":"

                    vTable.add_row([vSiblingType, pl.NoEscape(hlt.GetPersonNameWithReference(vSiblingData[3][1], vSiblingData[3][0], vSiblingData[1]))])

            self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WritePartnerSubsections(self):
        # Add families with partners
        for vPartnerHandle in self.__PartnerHandleList:
            if(vPartnerHandle is not None):  # TODO: Also handle families with unknown partners
                vPartnerData = DecodePersonData(vPartnerHandle, self.__Cursor)
                vPartnerGrampsId = vPartnerData[1]
                vPartnerSurname = vPartnerData[3][0]
                vPartnerGivenNames = vPartnerData[3][1]

                # For each partner create a sub section
                self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
                with self.__Chapter.create(pl.Subsection(title=pl.NoEscape(hlt.GetPersonNameWithReference(vPartnerGivenNames, vPartnerSurname, vPartnerGrampsId)), label=False)):
                    if(self.__Gender == 0):
                        vFamilyHandle = GetFamilyHandleByFatherMother(vPartnerHandle, self.__PersonHandle, self.__Cursor)
                    else:
                        vFamilyHandle = GetFamilyHandleByFatherMother(self.__PersonHandle, vPartnerHandle, self.__Cursor)

                    if(vFamilyHandle is not None):
                        vFamilyHandle = vFamilyHandle[0]

                        # Nieuw
                        vFamilyInfo = DecodeFamilyData(vFamilyHandle, self.__Cursor)
                        vFamilyGrampsId = vFamilyInfo[0]
                        vFamilyEventRefList = vFamilyInfo[5]

                        vFamilyEventInfoDict = {}
                        for vFamilyEventRef in vFamilyEventRefList:
                            vFamilyEventHandle = vFamilyEventRef[3]
                            vFamilyEventInfo = DecodeEventData(vFamilyEventHandle, self.__Cursor)
                            if(vFamilyEventInfo[0] in vFamilyEventInfoDict):
                                vFamilyEventInfoDict[vFamilyEventInfo[0]].append(vFamilyEventInfo[1:])
                            else:
                                vFamilyEventInfoDict[vFamilyEventInfo[0]] = [vFamilyEventInfo[1:]]

                        # OUD
                        vFamilyEvents = vFamilyEventsSet.intersection(vFamilyEventInfoDict.keys())
                        if(vFamilyEvents):
                            with self.__Chapter.create(pl.Subsubsection(title=hlg.Translate('family events', self.__language), label=False)):
                                with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                                    for vEvent in vFamilyEvents:
                                        vString_1 = "Date of " + vEventTypeDict[vEvent]
                                        vString_2 = "Place of " + vEventTypeDict[vEvent]
                                        vTable.add_row([hlg.Translate(vString_1, self.__language) + ":", DateToText(vFamilyEventInfoDict[vEvent][0][0], False)])
                                        vTable.add_row([hlg.Translate(vString_2, self.__language) + ":", vFamilyEventInfoDict[vEvent][0][1]])

                                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

                        # Add subchapter for children
                        vChildrenHandles = GetChildrenHandlesByFamily(vFamilyHandle, self.__Cursor)
                        if(len(vChildrenHandles) > 0):
                            # If children exist, then create sub chapter and a
                            # table
                            with self.__Chapter.create(pl.Subsubsection(title=hlg.Translate('children', self.__language), label=False)):
                                with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                                    for vChildHandle in vChildrenHandles:
                                        # For each child create a separate row
                                        # in the table
                                        vChildData = DecodePersonData(vChildHandle, self.__Cursor)
                                        if(vChildData[2] == 0):
                                            vChildType = hlg.Translate('daughter', self.__language) + ":"
                                        elif(vChildData[2] == 1):
                                            vChildType = hlg.Translate('son', self.__language) + ":"
                                        else:
                                            vChildType = hlg.Translate('unknown', self.__language) + ":"

                                        vTable.add_row([vChildType, pl.NoEscape(hlt.GetPersonNameWithReference(vChildData[3][1], vChildData[3][0], vChildData[1]))])

                                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteFamilySection(self):
        # Create section with Family Information
        self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
        with self.__Chapter.create(pl.Section(title=hlg.Translate('family', self.__language), label=False)):
            self.__WriteParentalSubsection()
            self.__WritePartnerSubsections()

    def __WriteEducationSection(self):
        # Create section with Education ***
        vEducationEvents = vEducationEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vEducationEvents):
            vEducationList = []
            for vEvent in vEducationEvents:
                vEducationList = vEducationList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vEducationList.sort(key=vDateFunc)

            self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
            with self.__Chapter.create(pl.Section(title=hlg.Translate('education', self.__language), label=False)):
                with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('course', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    # Add row for each event
                    for vEducation in vEducationList:
                        if(len(vEducation[2]) == 0):
                            vEducation[2] = '-'

                        vTable.add_row([DateToText(vEducation[0]), pl.NoEscape(vEducation[2]) + pl.NoEscape(r'\newline ') + pu.escape_latex(vEducation[1])])

                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteProfessionSection(self):
        # Create section with Working Experience ***
        vProfessionalEvents = vProfessionalEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vProfessionalEvents):
            vProfessionalList = []
            for vEvent in vProfessionalEvents:
                vProfessionalList = vProfessionalList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vProfessionalList.sort(key=vDateFunc)

            self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
            with self.__Chapter.create(pl.Section(title=hlg.Translate('occupation', self.__language), label=False)):
                with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('profession', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    # Add row for each event
                    for vProfession in vProfessionalList:
                        if(len(vProfession[2]) == 0):
                            vProfession[2] = '-'

                        vTable.add_row([DateToText(vProfession[0]), pu.escape_latex(vProfession[2]) + pl.NoEscape(r'\newline ') + pu.escape_latex(vProfession[1])])

                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteResidenceSection(self):
        # Create section with Residential Information
        vResidentialEvents = vResidentialEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vResidentialEvents):
            vResidenceList = []
            for vEvent in vResidentialEvents:
                vResidenceList = vResidenceList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vResidenceList.sort(key=vDateFunc)

            self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
            with self.__Chapter.create(pl.Section(title=hlg.Translate('residences', self.__language), label=False)):
                with self.__Chapter.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('residence', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    for vResidence in vResidenceList:
                        vTable.add_row([DateToText(vResidence[0]), pu.escape_latex(vResidence[1])])

                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WritePhotoSection(self):
        """
        Create section with photos
        """

        vFilteredPhotoList = self.__GetFilteredPhotoList()
        if(len(vFilteredPhotoList) > 0):
            self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
            with self.__Chapter.create(pl.Section(title=hlg.Translate('photos', self.__language), label=False)):
                # Use temporary lsit, so items can be removed while iterating
                vTempList = vFilteredPhotoList.copy()
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vNoteHandleList = vMediaData[8]
                    if(len(vNoteHandleList) > 0):
                        # if picture contains notes, then special treatment
                        self.__PictureWithNote(vMediaData)

                        # Done, remove from list
                        vFilteredPhotoList.remove(vMediaHandle)
                    else:
                        # check on landscape vs portrait
                        vImage = Image.open(vMediaData[2], mode='r')
                        vWidth, vHeight = vImage.size
                        if(vWidth > vHeight):
                            # landscape photo without notes, process now
                            self.__Chapter.append(pl.NoEscape(r'\begin{figure}[h]'))
                            with self.__Chapter.create(pl.MiniPage(width=r"\textwidth")) as vMiniPage:
                                vMiniPage.append(pl.NoEscape(r'\centering'))
                                vMiniPage.append(pl.NoEscape(r'\includegraphics[width=\textwidth]{"' + vMediaData[2] + r'"}'))
                                vMiniPage.append(pl.NoEscape(r'\caption{' + pu.escape_latex(vMediaData[4]) + r'}'))

                            self.__Chapter.append(pl.NoEscape(r'\end{figure}'))

                            # Done, remove from list
                            vFilteredPhotoList.remove(vMediaHandle)

                # process remainder photos in the list, i.e. all portrait
                # photos without notes
                vCounter = 0

                # Use temporary list, so items can be removed while iterating
                vTempList = vFilteredPhotoList.copy()
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vCounter = vCounter + 1
                    if (vCounter % 2 == 1):
                        vMediaData_1 = vMediaData
                    else:
                        vMediaData_2 = vMediaData
                        self.__PictureSideBySideEqualHeight(vMediaData_1, vMediaData_2)

                        # Done, remove media_1 and edia_2 from list
                        vFilteredPhotoList.remove(vMediaData_1[0])
                        vFilteredPhotoList.remove(vMediaData_2[0])

                # In case the remainder list had an odd length, process the
                # remaining 1 portrait photo
                if(len(vFilteredPhotoList) > 1):
                    print("ERROR in __WritePhotoSection: Remaining photo list > 1")
                elif(len(vFilteredPhotoList) == 1):
                    vMediaHandle = vFilteredPhotoList[0]
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    self.__Chapter.append(pl.NoEscape(r'\begin{figure}[h]'))
                    with self.__Chapter.create(pl.MiniPage(width=r"0.5\textwidth")) as vMiniPage:
                        vMiniPage.append(pl.NoEscape(r'\centering'))
                        vMiniPage.append(pl.NoEscape(r'\includegraphics[width=0.9\textwidth]{"' + vMediaData[2] + r'"}'))
                        vMiniPage.append(pl.NoEscape(r'\caption{' + pu.escape_latex(vMediaData[4]) + r'}'))

                    self.__Chapter.append(pl.NoEscape(r'\end{figure}'))
                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteDocumentSection(self):
        """
        Create section with photos
        """

        vFilteredDocumentList = self.__GetFilteredDocumentList()
        if(len(vFilteredDocumentList) > 0):
            self.__Chapter.append(pl.NoEscape(r"\needspace{\minspace}"))
            with self.__Chapter.create(pl.Section(title=hlg.Translate('documents', self.__language), label=False)):
                # Use temporary list, so items can be removed while iterating
                vTempList = vFilteredDocumentList.copy()
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vNoteHandleList = self.__GetFilteredNoteList(vMediaData[8])

                    # TODO: dit gaat mis als het om een note met tag 'source' gaat
                    if(len(vNoteHandleList) > 0):
                        # if document contains notes, then special treatment
                        #						self.__PictureWithNote(vMediaData)
                        self.__DocumentWithNote(vMediaData)

                        # Done, remove from list
                        vFilteredDocumentList.remove(vMediaHandle)
                    else:
                        # check on landscape vs portrait
                        vImage = Image.open(vMediaData[2], mode='r')
                        vWidth, vHeight = vImage.size
                        if(vWidth > vHeight):
                            # landscape photo without notes, process now
                            self.__Chapter.append(
                                pl.NoEscape(r'\begin{figure}[h]'))
                            with self.__Chapter.create(pl.MiniPage(width=r"\textwidth")) as vMiniPage:
                                vMiniPage.append(pl.NoEscape(r'\centering'))
                                vMiniPage.append(pl.NoEscape(r'\includegraphics[width=\textwidth]{"' + vMediaData[2] + r'"}'))
                                vMiniPage.append(pl.NoEscape(r'\caption{' + pu.escape_latex(vMediaData[4]) + r'}'))

                            self.__Chapter.append(pl.NoEscape(r'\end{figure}'))

                            # Done, remove from list
                            vFilteredDocumentList.remove(vMediaHandle)

                # process remainder photos in the list, i.e. all portrait
                # photos without notes
                vCounter = 0
                # Use temporary list, so items can be removed while iterating
                vTempList = vFilteredDocumentList.copy()
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vCounter = vCounter + 1
                    if (vCounter % 2 == 1):
                        vMediaData_1 = vMediaData
                    else:
                        vMediaData_2 = vMediaData
                        self.__PictureSideBySideEqualHeight(
                            vMediaData_1, vMediaData_2)

                        # Done, remove media_1 and media_2 from list
                        vFilteredDocumentList.remove(vMediaData_1[0])
                        vFilteredDocumentList.remove(vMediaData_2[0])

                # In case the remainder list had an odd length, process the
                # remaining 1 portrait document
                if(len(vFilteredDocumentList) > 1):
                    print(
                        "ERROR in __WriteDocumentSection: Remaining document list > 1")
                elif(len(vFilteredDocumentList) == 1):
                    vMediaHandle = vFilteredDocumentList[0]
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    self.__Chapter.append(pl.NoEscape(r'\begin{figure}[h]'))
                    with self.__Chapter.create(pl.MiniPage(width=r"0.5\textwidth")) as vMiniPage:
                        vMiniPage.append(pl.NoEscape(r'\centering'))
                        vMiniPage.append(pl.NoEscape(r'\includegraphics[width=\textwidth]{"' + vMediaData[2] + r'"}'))
                        vMiniPage.append(pl.NoEscape(r'\caption{' + pu.escape_latex(vMediaData[4]) + r'}'))

                    self.__Chapter.append(pl.NoEscape(r'\end{figure}'))
                self.__Chapter.append(pl.NoEscape(r'\FloatBarrier'))

    def WritePersonChapter(self):
        """
        Writes the person to a separate chapter in a subdocument
        """

        # Display progress
        print("Writing a chapter about: ", self.GivenNames, self.Surname)

        # Create a new chapter for the active person
        self.__Chapter = hlt.Chapter(
            title=self.GivenNames + ' ' + self.Surname,
            label=self.GrampsId)

        self.__WriteLifeSketchSection()
        self.__WriteVitalInformationSection()
        self.__WriteFamilySection()
        self.__WriteEducationSection()
        self.__WriteProfessionSection()
        self.__WriteResidenceSection()
        self.__WritePhotoSection()
        self.__WriteDocumentSection()

        self.__Chapter.generate_tex(filepath=self.DocumentPath + self.GrampsId)
