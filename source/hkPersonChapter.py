# Formatted using "python3-autopep8 --in-place --aggressive --aggressive *.py"

import bbCountries as bbc

import hkLanguage as hlg
import hkLatex as hlt

from hkGrampsDb import *
import hkSupportFunctions as hsf

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc

from PIL import Image
# Prevents PIL.Image.DecompressionBombError: Image size (... pixels)
# exceeds limit of .... pixels, could be decompression bomb DOS attack.
Image.MAX_IMAGE_PIXELS = None

import os

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
        self.__SiblingHandlesList = hsf.SortPersonListByBirth(GetSiblingHandles_Old(self.__PersonHandle, self.__Cursor), self.__Cursor)

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
        """ Checks whether scans are avaiable for the events birth, marriage and death """

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

                # 1 = Marriage, 2 = Marriage Settlement, 3 = Marriage License, 4 = Marriage Contract
                if((vType == vEventMarriage or vType == vEventMarriageSettlement or vType == vEventMarriageLicense or vType == vEventMarriageContract) and (len(vMediaList) > 0)):
                    vSourceStatus['m'] = 'm'

        # Death / Burial
        vMediaList = []
        if(vEventDeath in self.__PersonEventInfoDict):  # Death
            vEventInfo = self.__PersonEventInfoDict[vEventDeath]
            vMediaList.extend(vEventInfo[0][3])

        if(vEventBurial in self.__PersonEventInfoDict): # Burial
            vEventInfo = self.__PersonEventInfoDict[vEventBurial]
            vMediaList.extend(vEventInfo[0][3])

        if(len(vMediaList) > 0):
            vSourceStatus['d'] = 'd'

        return vSourceStatus

    def __PictureWithNote(self, pLevel, pImagePath, pImageTitle, pImageNoteHandles):
        self.__DocumentWithNote(pLevel, pImagePath, pImageTitle, pImageNoteHandles)

    def __DocumentWithNote(self, pLevel, pImagePath, pImageTitle, pImageNoteHandles, pImageRect = None):
        # Add note(s)
        vNoteText = ''
        for vNoteHandle in pImageNoteHandles:
            vNoteData = DecodeNoteData(vNoteHandle, self.__Cursor)
            vTempText = vNoteData[2][0]

            # Check whether the note concerns a web address
            if(vTempText[:4] == "http"):
                # ..it does, first find '//'..
                vPos = vTempText.find('//')

                # ..from that position find the next '/'
                vPos = vTempText.find('/', vPos+2)

                # ..and create a link..
                vNoteText = vNoteText + r'Link to source: \href{' + vTempText + '}{' + vTempText[:vPos-1] + r'}' + r'\par '
            else:
                vNoteText = vNoteText + vTempText + r' \par '
#            vTagHandleList = vNoteData[6]

        # Check on portait vs landscape
        vImage = Image.open(pImagePath, mode='r')
        vWidth, vHeight = vImage.size

        # HIER: Work in progress
#        if(pImageRect is not None):
#            vWidth = vWidth * (pImageRect[2] - pImageRect[0])/100
#            vHeight = vHeight * (pImageRect[3] - pImageRect[1])/100

        if(vWidth > vHeight):
            # Landscape
            with pLevel.create(hlt.Figure()) as vFigure:
                vFigure.add_image(filename=pImagePath)
                vFigure.add_caption(pu.escape_latex(pImageTitle))
        else:
            # Portrait
            hsf.WrapFigure(pLevel, pFilename=pImagePath, pCaption=pImageTitle, pWidth=r'0.50\textwidth', pText=vNoteText)

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
            vMediaRect   = vMediaItem[5] # corner1 and corner 2 in Media Reference Editor in Gramps
            vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
            vMediaMime = vMediaData[3]
            vTagHandleList = vMediaData[11]

            if((vMediaMime.lower() == 'image/jpeg') or (vMediaMime.lower() == 'image/png')):
                if (cPublishable in GetTagList(vTagHandleList, self.__TagDictionary)) and (cDocument in GetTagList(vTagHandleList, self.__TagDictionary)):
                    vDocumentList.append([vMediaHandle, vMediaRect])

        return vDocumentList

    def __GetFilteredDocumentList_Old(self):
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

    def __WriteLifeSketchSection(self, pLevel):
        # Create section with Life Sketch
        pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))

        with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('life sketch', self.__language), pLabel=False) as vSubLevel:
            # Create a story line
            vLifeSketch = ""

            # Check whether lifestories already exist in the notes
            for vNote in self.__NoteBase:
                vNoteHandle = vNote
                vNoteData = DecodeNoteData(vNoteHandle, self.__Cursor)
                vNoteText = vNoteData[2][0]
                vNoteType = vNoteData[4][0]
                if(vNoteType == vNotePerson):  # Person Note
                    vLifeSketch = vLifeSketch + pu.escape_latex(vNoteText)

            # If no specific life stories were found, then write one
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
                    vString = hlg.Translate("{0} was born on {1}", self.__language).format(pu.escape_latex(vFullName), hsf.DateToText(self.__PersonEventInfoDict[vEventBirth][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBirth][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBirth][0][1] != '-')):
                        vString = hlg.Translate("in {0}", self.__language).format(hsf.PlaceToText(self.__PersonEventInfoDict[vEventBirth][0][1]))
                        vLifeSketch = vLifeSketch + ' ' + vString

                    vLifeSketch = vLifeSketch + r". "

                elif(vEventBaptism in vVitalEvents):  # Baptism
                    vString = hlg.Translate("{0} was born about {1}", self.__language).format(pu.escape_latex(vFullName), hsf.DateToText(self.__PersonEventInfoDict[vEventBaptism][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBaptism][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBaptism][0][1] != '-')):
                        vString = hlg.Translate("in {0}", self.__language).format(hsf.PlaceToText(self.__PersonEventInfoDict[vEventBaptism][0][1]))
                        vLifeSketch = vLifeSketch + ' ' + vString

                    vLifeSketch = vLifeSketch + r". "

                # Roepnaam
                vUseName = self.__GivenNames
                if(len(self.__CallName) > 0):
                    vUseName = self.__CallName
                    vString = hlg.Translate("{0} call name was {1}.", self.__language).format(vHisHer, pu.escape_latex(self.__CallName))
                    vLifeSketch = vLifeSketch + vString

                if(len(vLifeSketch) > 0):
                    vLifeSketch = vLifeSketch + r"\par "

                # Sisters and brothers
                vNumberSisters = 0
                vNumberBrothers = 0
                vSiblingNames = []
                vHasSiblings = False
                for vSiblingHandle in self.__SiblingHandlesList:
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
                    vLifeSketch = vLifeSketch + r"\par "
                elif(len(vSiblingNames) == 1):
                    vLifeSketch = vLifeSketch + pu.escape_latex(vSiblingNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\par "

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
                        vLifeSketch = vLifeSketch + hlg.Translate("one son:", self.__language) + ' '
                    else:
                        vString = hlg.Translate("{0} sons:", self.__language).format(vNumberSons)
                        vLifeSketch = vLifeSketch + vString + ' '

                if(len(vChildNames) > 1):
                    for vChildName in vChildNames[:-1]:
                        vLifeSketch = vLifeSketch + pu.escape_latex(vChildName) + ", "

                    vLifeSketch = vLifeSketch + hlg.Translate("and", self.__language) + ' ' + pu.escape_latex(vChildNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\par "
                elif(len(vChildNames) == 1):
                    vLifeSketch = vLifeSketch + pu.escape_latex(vChildNames[-1]) + ". "
                    vLifeSketch = vLifeSketch + r"\par "


                # Overlijden
                if(vEventDeath in vVitalEvents):  # Death
                    vString = hlg.Translate("{0} died on {1}", self.__language).format(vHeShe, hsf.DateToText(self.__PersonEventInfoDict[vEventDeath][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventDeath][0][1]) > 0) and (self.__PersonEventInfoDict[vEventDeath][0][1] != '-')):
                        vString = hlg.Translate("in {0}.", self.__language).format(hsf.PlaceToText(self.__PersonEventInfoDict[vEventDeath][0][1]))
                        vLifeSketch = vLifeSketch + ' ' + vString
                    else:
                        vLifeSketch = vLifeSketch + ". "

                elif(vEventBurial in vVitalEvents):  # Burial
                    vString = hlg.Translate("{0} died about {1}", self.__language).format(vHeShe, hsf.DateToText(self.__PersonEventInfoDict[vEventBurial][0][0], False))
                    vLifeSketch = vLifeSketch + vString

                    if((len(self.__PersonEventInfoDict[vEventBurial][0][1]) > 0) and (self.__PersonEventInfoDict[vEventBurial][0][1] != '-')):
                        vString = hlg.Translate("and was buried in {0}.", self.__language).format(hsf.PlaceToText(self.__PersonEventInfoDict[vEventBurial][0][1]))
                        vLifeSketch = vLifeSketch + ' ' + vString + ' '
                    else:
                        vLifeSketch = vLifeSketch + ". "

            vLifeSketch = vLifeSketch.replace(r"\n\n","\par") # Replace double newline characters with \par
            vLifeSketch = vLifeSketch.replace(r"\newline%\newline","\par") # Replace double newline characters with \par

            vPortraitFound = False
            for vMediaItem in self.__MediaList:
                vMediaHandle = vMediaItem[4]
                vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                vMediaPath = vMediaData[2]
                vMediaMime = vMediaData[3]
                vMediaDescription = vMediaData[4]
                vTagHandleList = vMediaData[11]

                if ('Portrait' in GetTagList(vTagHandleList, self.__TagDictionary)):
                    vPortraitFound = True
                    hsf.WrapFigure(vSubLevel, pFilename=vMediaPath, pWidth=r'0.35\textwidth', pText=vLifeSketch)

            if(not vPortraitFound):
                vSubLevel.append(pl.NoEscape(vLifeSketch))

        vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))


    def __WriteVitalInformationSection(self, pLevel):
        # Create section with Vital Information
        pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('vital information', self.__language), pLabel=False) as vSubLevel:
            with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                if(len(self.__CallName) > 0):
                    vTable.add_row([hlg.Translate('call name', self.__language) + ":", self.__CallName])

                if(self.__Gender in vGenderDict):
                    vTable.add_row([hlg.Translate('gender', self.__language) + ":", hlg.Translate(vGenderDict[self.__Gender], self.__language)])

                for vEvent in self.__PersonEventInfoDict.keys():
                    if (vEvent in vVitalEventsSet):
                        vString_1 = "Date of " + vEventTypeDict[vEvent]
                        vString_2 = "Place of " + vEventTypeDict[vEvent]

                        vString3 = hsf.DateToText(self.__PersonEventInfoDict[vEvent][0][0], False)
                        vString4 = hsf.PlaceToText(self.__PersonEventInfoDict[vEvent][0][1], True)

                        if(len(vString3)>0): vTable.add_row([hlg.Translate(vString_1, self.__language) + ":", vString3])
                        if(len(vString4)>0): vTable.add_row([hlg.Translate(vString_2, self.__language) + ":", vString4])

            vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteParentalSection_Graph(self, pLevel):
        # Add Family graph
        pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('parental family', self.__language), pLabel=False) as vSubLevel:
            # Create a sorted list of self and siblings
            vSiblingList = []
            vSiblingList.append(self.__PersonHandle)

            for vSiblingHandle in self.__SiblingHandlesList:
                vSiblingList.append(vSiblingHandle)

            vSiblingList = hsf.SortPersonListByBirth(vSiblingList, self.__Cursor)

            # Create nodes
            vSubLevel.append(pu.NoEscape(r'\begin{tikzpicture}'))
            vSubLevel.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

            # Parents
            vFatherName = hlg.Translate('Unknown', self.__language)
            if(self.__FatherHandle is not None):
                vFatherData = DecodePersonData(self.__FatherHandle, self.__Cursor)
                vFatherName = pl.NoEscape(hlt.GetPersonNameWithReference(vFatherData[3][1], vFatherData[3][0], vFatherData[1]))

            vMotherName = hlg.Translate('Unknown', self.__language)
            if(self.__MotherHandle is not None):
                vMotherData = DecodePersonData(self.__MotherHandle, self.__Cursor)
                vMotherName = pl.NoEscape(hlt.GetPersonNameWithReference(vMotherData[3][1], vMotherData[3][0], vMotherData[1]))

            # First row
            vSubLevel.append(pu.NoEscape(r'\node (father) [left, man]    {\small ' + vFatherName + r'}; &'))
            vSubLevel.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
            vSubLevel.append(pu.NoEscape(r'\node (mother) [right, woman] {\small ' + vMotherName + r'};\\'))

            # Empty row
            vString = r' & & \\'
            vSubLevel.append(pu.NoEscape(vString))

            # Next one row per sibling
            vCounter = 0
            for vSiblingHandle in vSiblingList:
                vCounter       = vCounter + 1
                vSiblingData   = DecodePersonData(vSiblingHandle, self.__Cursor)
                vSiblingId     = vSiblingData[1]
                vSiblingGender = vSiblingData[2]

                if(vSiblingId == self.__GrampsId):
                    vSiblingName = self.__GivenNames + ' ' + self.__Surname
                else:
                    vSiblingName = pl.NoEscape(hlt.GetPersonNameWithReference(vSiblingData[3][1], vSiblingData[3][0], vSiblingData[1]))

                vString = ''
                if(vSiblingGender == 0): # Female
                    vString = r' & & \node (p' + str(vCounter) + r') [right, woman'
                elif(vSiblingGender == 1): # Male
                    vString = r' & & \node (p' + str(vCounter) + r') [right, man'
                else:
                    vString = r' & & \node (p' + str(vCounter) + r') [right, man'

                if(vSiblingId == self.__GrampsId):
                    vString = vString + r', self'

                vString = vString + r'] {\small ' + vSiblingName + r'}; \\'
                vSubLevel.append(pu.NoEscape(vString))

            vSubLevel.append(pu.NoEscape(r'};'))

            # Create the graph
            vSubLevel.append(pu.NoEscape(r'\graph [use existing nodes] {'))
            vSubLevel.append(pu.NoEscape(r'father -- p0 -- mother;'))

            for vCount in range(1, vCounter + 1):
                vSubLevel.append(pu.NoEscape(r'p0 -> [vh path] p' + str(vCount) + r';'))

            vSubLevel.append(pu.NoEscape(r'};'))
            vSubLevel.append(pu.NoEscape(r'\end{tikzpicture}'))
            vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteParentalSubsection_Table(self, pLevel):
        # Add Family table
        pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('parental family', self.__language), pLabel=False) as vSubLevel:
            with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                vFatherName = hlg.Translate('Unknown', self.__language)
                if(self.__FatherHandle is not None):
                    vFatherData = DecodePersonData(self.__FatherHandle, self.__Cursor)
                    vFatherName = pl.NoEscape(hlt.GetPersonNameWithReference(vFatherData[3][1], vFatherData[3][0], vFatherData[1]))

                vTable.add_row([hlg.Translate('father', self.__language) + ":", vFatherName])

                vMotherName = hlg.Translate('Unknown', self.__language)
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

            vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WritePartnerSections_Graph(self, pLevel):
        # Add families with partners
        for vPartnerHandle in self.__PartnerHandleList:
            if(vPartnerHandle is not None):  # TODO: Also handle families with unknown partners
                vPartnerData = DecodePersonData(vPartnerHandle, self.__Cursor)
                vPartnerGrampsId = vPartnerData[1]
                vPartnerSurname = vPartnerData[3][0]
                vPartnerGivenNames = vPartnerData[3][1]

                # For each partner create a sub section
                pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hlt.CreateSubLevel(pLevel=pLevel, pTitle=pl.NoEscape(hlt.GetPersonNameWithReference(vPartnerGivenNames, vPartnerSurname, vPartnerGrampsId)), pLabel=False) as vSubLevel:
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
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.Translate('family events', self.__language), pLabel=False) as vSubSubLevel:
                                with vSubSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                                    for vEvent in vFamilyEvents:
                                        vString_1 = "Date of " + vEventTypeDict[vEvent]
                                        vString_2 = "Place of " + vEventTypeDict[vEvent]
                                        vString_3 = hsf.DateToText(vFamilyEventInfoDict[vEvent][0][0], False)
                                        vString_4 = hsf.PlaceToText(vFamilyEventInfoDict[vEvent][0][1], True)

                                        if(len(vString_3)>0): vTable.add_row([hlg.Translate(vString_1, self.__language) + ":", vString_3])
                                        if(len(vString_4)>0): vTable.add_row([hlg.Translate(vString_2, self.__language) + ":", vString_4])

                                vSubSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

                            # Add subchapter for children
                            vChildrenHandles = GetChildrenHandlesByFamily(vFamilyHandle, self.__Cursor)
                            if(len(vChildrenHandles) > 0):
                                # If children exist, then create sub chapter and a table
                                with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.Translate('children', self.__language), pLabel=False) as vSubSubLevel:
                                    vFatherString = ''
                                    vMotherString = ''

                                    vSubSubLevel.append(pu.NoEscape(r'\begin{tikzpicture}'))
                                    vSubSubLevel.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                                    # Self
                                    vName = pl.NoEscape(self.GivenNames + ' ' + self.__Surname)
                                    if(self.__Gender == 0): # Female
                                        vMotherString = r'\node (mother) [right, woman, self] {\small ' + vName + r'};'
                                    else: # Male
                                        vFatherString = r'\node (father) [left, man, self] {\small ' + vName + r'};'

                                    # Partner
                                    vName = pl.NoEscape(hlt.GetPersonNameWithReference(vPartnerData[3][1], vPartnerData[3][0], vPartnerData[1]))
                                    if(vPartnerData[2] == 0): # Female
                                        vMotherString = r'\node (mother) [right, woman] {\small ' + vName + r'};'
                                    else: # Male
                                        vFatherString = r'\node (father) [left, man] {\small ' + vName + r'};'

                                    # First row
                                    vSubSubLevel.append(pu.NoEscape(vFatherString + r' &'))
                                    vSubSubLevel.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
                                    vSubSubLevel.append(pu.NoEscape(vMotherString + r' \\'))

                                    # Empty row
                                    vString = r' & & \\'
                                    vSubSubLevel.append(pu.NoEscape(vString))

                                    # Next one row per child
                                    vCounter = 0

                                    # Children
                                    for vChildHandle in vChildrenHandles:
                                        vCounter = vCounter + 1
                                        vChildData = DecodePersonData(vChildHandle, self.__Cursor)
                                        vChildName = pl.NoEscape(hlt.GetPersonNameWithReference(vChildData[3][1], vChildData[3][0], vChildData[1]))

                                        vString = ''
                                        if(vChildData[2] == 0): # Female
                                            vString = r' & & \node (p' + str(vCounter) + r') [right, woman] {\small ' + vChildName + r'}; \\'
                                        elif(vChildData[2] == 1): # Male
                                            vString = r' & & \node (p' + str(vCounter) + r') [right, man] {\small ' + vChildName + r'}; \\'
                                        else:
                                            vString = r' & & \node (p' + str(vCounter) + r') [right, man] {\small ' + vChildName + r'}; \\'

                                        vSubSubLevel.append(pu.NoEscape(vString))

                                    vSubSubLevel.append(pu.NoEscape(r'};'))

                                    # Create the graph
                                    vSubSubLevel.append(pu.NoEscape(r'\graph [use existing nodes] {'))
                                    vSubSubLevel.append(pu.NoEscape(r'father -- p0 -- mother;'))

                                    for vCount in range(1, vCounter + 1):
                                        vSubSubLevel.append(pu.NoEscape(r'p0 -> [vh path] p' + str(vCount) + r';'))

                                    vSubSubLevel.append(pu.NoEscape(r'};'))
                                    vSubSubLevel.append(pu.NoEscape(r'\end{tikzpicture}'))
                                    vSubSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WritePartnerSections_Table(self, pLevel):
        # Add families with partners
        for vPartnerHandle in self.__PartnerHandleList:
            if(vPartnerHandle is not None):  # TODO: Also handle families with unknown partners
                vPartnerData = DecodePersonData(vPartnerHandle, self.__Cursor)
                vPartnerGrampsId = vPartnerData[1]
                vPartnerSurname = vPartnerData[3][0]
                vPartnerGivenNames = vPartnerData[3][1]

                # For each partner create a sub section
                pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hlt.CreateSubLevel(pLevel=pLevel, pTitle=pl.NoEscape(hlt.GetPersonNameWithReference(vPartnerGivenNames, vPartnerSurname, vPartnerGrampsId)), pLabel=False) as vSubLevel:
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
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.Translate('family events', self.__language), pLabel=False) as vSubSubLevel:
                                with vSubSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                                    for vEvent in vFamilyEvents:
                                        vString_1 = "Date of " + vEventTypeDict[vEvent]
                                        vString_2 = "Place of " + vEventTypeDict[vEvent]
                                        vTable.add_row([hlg.Translate(vString_1, self.__language) + ":", hsf.DateToText(vFamilyEventInfoDict[vEvent][0][0], False)])
                                        vTable.add_row([hlg.Translate(vString_2, self.__language) + ":", hsf.PlaceToText(vFamilyEventInfoDict[vEvent][0][1], True)])

                                vSubSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

                        # Add subchapter for children
                        vChildrenHandles = GetChildrenHandlesByFamily(vFamilyHandle, self.__Cursor)
                        if(len(vChildrenHandles) > 0):
                            # If children exist, then create sub chapter and a table
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.Translate('children', self.__language), pLabel=False) as vSubSubLevel:
                                with vSubSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
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

                                vSubSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteFamilySection(self, pLevel):
        """
        Create a section listing all family relationships
        """

        # Create section with Family Information
        pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
        with pLevel.create(hlt.Section(title=hlg.Translate('family', self.__language), label=False)) as vSubLevel:
            self.__WriteParentalSection_Graph(vSubLevel)
            self.__WritePartnerSections_Graph(vSubLevel)

    def __WriteEducationSection(self, pLevel):
        """
        Create a section with a table containing education
        """

        # Create section with Education ***
        vEducationEvents = vEducationEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vEducationEvents):
            vEducationList = []
            for vEvent in vEducationEvents:
                vEducationList = vEducationList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vEducationList.sort(key=vDateFunc)

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('education', self.__language), pLabel=False) as vSubLevel:
                with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('course', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    # Add row for each event
                    for vEducation in vEducationList:
                        if(len(vEducation[2]) == 0):
                            vEducation[2] = '-'

                        vDate   = hsf.DateToText(vEducation[0])
                        vCourse = vEducation[2]
                        vPlace  = hsf.PlaceToText(vEducation[1], True)
                        vTable.add_row([vDate, pl.NoEscape(vCourse) + pl.NoEscape(r'\newline ') + pu.escape_latex(vPlace)])

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteProfessionSection(self, pLevel):
        """
        Create a section with a table containing working experiences
        """

        # Create section with Working Experience ***
        vProfessionalEvents = vProfessionalEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vProfessionalEvents):
            vProfessionalList = []
            for vEvent in vProfessionalEvents:
                vProfessionalList = vProfessionalList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vProfessionalList.sort(key=vDateFunc)

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('occupation', self.__language), pLabel=False) as vSubLevel:
                with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('profession', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    # Add row for each event
                    for vProfession in vProfessionalList:
                        if(len(vProfession[2]) == 0):
                            vProfession[2] = '-'

                        vDate   = hsf.DateToText(vProfession[0])
                        vJob    = vProfession[2]
                        vPlace  = hsf.PlaceToText(vProfession[1], True)
                        vTable.add_row([vDate, pu.escape_latex(vJob) + pl.NoEscape(r'\newline ') + pu.escape_latex(vPlace)])

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteResidenceSection_Map(self, pLevel):
        """
        Create a section with maps of all residences
        """

        #
        # Work in Progress
        #

        # Create section with Residential Information
        vResidentialEvents = vResidentialEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vResidentialEvents):
            # Create path name for map
            vPath = self.__DocumentPath + r'Figures'

            # Compose some temporary place type labeles
            vCityLabel         = vPlaceTypeDict[vPlaceTypeCity]
            vTownLabel         = vPlaceTypeDict[vPlaceTypeTown]
            vVillageLabel      = vPlaceTypeDict[vPlaceTypeVillage]
            vMunicipalityLabel = vPlaceTypeDict[vPlaceTypeMunicipality]
            vCountryLabel      = vPlaceTypeDict[vPlaceTypeCountry]

            # Compose residence list
            vResidenceList = []
            for vEvent in vResidentialEvents:
                vResidenceList = vResidenceList + self.__PersonEventInfoDict[vEvent]

            # Create minipage
            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('residences', self.__language), pLabel=False) as vSubLevel:
                # Create Tikz drawing with map as background
#                    vSubLevel.append(pu.NoEscape(r'\begin{tikzpicture}'))

                # Create nodes
                vScopeOpen = False
                vDoneList  = []
                vCounter   = 0
                for vResidence in vResidenceList:
                    vCounter = vCounter + 1

                    # Split date  from place
                    vDate  = vResidence[0]
                    vPlace = vResidence[1]

                    # Find place name and coordinates
                    vName      = '-'
                    vLatitude  = 0.
                    vLongitude = 0.
                    vCode      = ''
                    if(vCityLabel in vPlace):
                        vName      = vPlace[vCityLabel][0]
                        vLatitude  = float(vPlace[vCityLabel][1][0])
                        vLongitude = float(vPlace[vCityLabel][1][1])
                        vCode      = vPlace[vCityLabel][2]
                    elif(vTownLabel in vPlace):
                        vName      = vPlace[vTownLabel][0]
                        vLatitude  = float(vPlace[vTownLabel][1][0])
                        vLongitude = float(vPlace[vTownLabel][1][1])
                        vCode      = vPlace[vTownLabel][2]
                    elif(vVillageLabel in vPlace):
                        vName      = vPlace[vVillageLabel][0]
                        vLatitude  = float(vPlace[vVillageLabel][1][0])
                        vLongitude = float(vPlace[vVillageLabel][1][1])
                        vCode      = vPlace[vVillageLabel][2]
                    elif(vMunicipalityLabel in vPlace):
                        vName      = vPlace[vMunicipalityLabel][0]
                        vLatitude  = float(vPlace[vMunicipalityLabel][1][0])
                        vLongitude = float(vPlace[vMunicipalityLabel][1][1])
                        vCode      = vPlace[vMunicipalityLabel][2]
                    else:
                        print('Warning in hkPersonChapter.__WriteResidenceSection_Map: No valid city/village found in vPlace: ', vPlace)

                    # Debug
#                        print('vName, vLongitude, vLatititude: ', vName, vLongitude, vLatitude)
                    
                    if(vCountryLabel in vPlace):
                        vCountry     = vPlace[vCountryLabel][0]
                        vCountryCode = vPlace[vCountryLabel][2]

                        if(len(vCountryCode)==0):
                            vCountryCode = vCountry

                    # 20220109: Limit number of maps to Netherlands, Western Europe and the World
                    if(vCountryCode != 'NLD'):
                        vRegionList = hsf.GetCountryContinentSubregion(vCountryCode)
                        if(vRegionList[1] == 'Western Europe'):
                            vCountryCode = 'WEU'
                        elif(vRegionList[0] == 'Europe'):
                            vCountryCode = 'EUR'
                        else:
                            vCountryCode = 'WLD'
                    
                    # Create path / file name for map
                    vPath = self.__DocumentPath + r'Figures'
                    vFilePath = hsf.CreateMap(vPath, vCountryCode)

                    if(vCountryCode not in vDoneList):
                        vDoneList.append(vCountryCode)

                        # Check if scope is still open
                        if(vScopeOpen):
                            vSubLevel.append(pu.NoEscape(r'\end{scope}'))
                            vSubLevel.append(pu.NoEscape(r'\end{tikzpicture}')) # 20220109
                            vScopeOpen = False

                        # Create node for background map
                        vSubLevel.append(pu.NoEscape(r'\begin{tikzpicture}')) # 20220109
                        vString = r'\node [inner sep=0] (' + vCountryCode + r') {\includegraphics[width=10cm]{' + vFilePath + r'}};'
                        vSubLevel.append(pu.NoEscape(vString))

                        # Create new scope with lower left corner (0,0) and upper right corner (1,1)
                        vString = r'\begin{scope}[x={(' + vCountryCode + r'.south east)},y={(' + vCountryCode + r'.north west)}]'
                        vSubLevel.append(pu.NoEscape(vString))
                        vScopeOpen = True

                    # width and height in degrees
                    vCoordinates = hsf.GetCountryMinMaxCoordinates(vCountryCode)
                    vMap_lon0 = vCoordinates[0]
                    vMap_lat0 = vCoordinates[1]
                    vMap_lon1 = vCoordinates[2]
                    vMap_lat1 = vCoordinates[3]

                    # Debug
#                        print('vMap_lon0, vMap_lat0, vMap_lon1, vMap_lat1: ', vMap_lon0, vMap_lat0, vMap_lon1, vMap_lat1)

                    # width and height in pixels
                    vMap_width = 0
                    vMap_height = 0
                    with Image.open(vFilePath, mode='r') as vImage:
                        vMap_width, vMap_height = vImage.size

                    # Debug
#                        print('vMap_width, vMap_height: ', vMap_width, vMap_height)

                    # Convert to image coordinates
                    vX = (vLongitude - vMap_lon0)/(vMap_lon1 - vMap_lon0) 
                    vY = (vLatitude - vMap_lat0)/(vMap_lat1 - vMap_lat0) 
                    if(vX<0 or vY<0):
                        print('Warning in hkPersonChapter.__WriteResidenceSection_Map: Place off map. vX, vY: ', vX, vY)

                    vString = r'\node (p' + str(vCounter) + r') at (' + str(vX) + r', ' + str(vY) +r') [point] {};'
                    vSubLevel.append(pu.NoEscape(vString))


                # Create graph
#                    vSubLevel.append(pu.NoEscape(r'\graph [use existing nodes] {'))
#
#                    for vCount in range(2, vCounter + 1):
#                        vSubLevel.append(pu.NoEscape(r'p' + str(vCount-1) + ' -> p' + str(vCount) + r';'))
#
#                    vSubLevel.append(pu.NoEscape(r'};'))
                if(vScopeOpen):
                    vSubLevel.append(pu.NoEscape(r'\end{scope}'))
                    vSubLevel.append(pu.NoEscape(r'\end{tikzpicture}'))
                    vScopeOpen = False

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteResidenceSection_Timeline(self, pLevel):
        """
        Create a section with a list of all residences in a graphical timeline format
        """

        # Create section with Residential Information
        vResidentialEvents = vResidentialEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vResidentialEvents):
            vResidenceList = []
            for vEvent in vResidentialEvents:
                vResidenceList = vResidenceList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vResidenceList.sort(key=vDateFunc)

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('residences', self.__language), pLabel=False) as vSubLevel:
                # Create nodes
                vSubLevel.append(pu.NoEscape(r'\begin{tikzpicture}'))
                vSubLevel.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                vCounter = 0
                for vResidence in vResidenceList:
                    vCounter = vCounter + 1

                    vStartDate = hsf.GetStartDate(vResidence[0])
                    vAddress   = hsf.StreetToText(vResidence[1])

                    vString = r'\node (p' + str(vCounter) + r') [date] {\small ' + vStartDate + r'}; & '
                    vString = vString + r'\node [text width=10cm] {\small ' + pu.escape_latex(vAddress) + r'};\\'
                    vSubLevel.append(pu.NoEscape(vString))

                vSubLevel.append(pu.NoEscape(r'};'))

                # Create graph
                vSubLevel.append(pu.NoEscape(r'\graph [use existing nodes] {'))

                for vCount in range(2, vCounter + 1):
                    vSubLevel.append(pu.NoEscape(r'p' + str(vCount-1) + ' -> p' + str(vCount) + r';'))

                vSubLevel.append(pu.NoEscape(r'};'))
                vSubLevel.append(pu.NoEscape(r'\end{tikzpicture}'))
                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteResidenceSection_Table(self, pLevel):
        """
        Create a section with a list of all residences in a table format
        """

        # Create section with Residential Information
        vResidentialEvents = vResidentialEventsSet.intersection(self.__PersonEventInfoDict.keys())
        if(vResidentialEvents):
            vResidenceList = []
            for vEvent in vResidentialEvents:
                vResidenceList = vResidenceList + self.__PersonEventInfoDict[vEvent]

            vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            vResidenceList.sort(key=vDateFunc)

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('residences', self.__language), pLabel=False) as vSubLevel:
                with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as vTable:
                    # Header row
                    vTable.add_row([pu.bold(hlg.Translate('date', self.__language)), pu.bold(hlg.Translate('residence', self.__language))])
                    vTable.add_hline()
                    vTable.end_table_header()

                    for vResidence in vResidenceList:
                        vDate    = hsf.DateToText(vResidence[0])
                        vAddress = hsf.StreetToText(vResidence[1])
                        vTable.add_row([vDate, pu.escape_latex(vAddress)])

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WritePhotoSection(self, pLevel):
        """
        Create section with photos
        """

        vFilteredPhotoList = self.__GetFilteredPhotoList()
        if(len(vFilteredPhotoList) > 0):
            # Allocate variables
            vMediaPath_1  = None
            vMediaTitle_1 = None
            vMediaPath_2  = None
            vMediaTitle_2 = None

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('photos', self.__language), pLabel=False) as vSubLevel:
                #
                # 1. All photos with notes
                #
                vTempList = vFilteredPhotoList.copy() # Use temporary list, so items can be removed while iterating
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vMediaPath = vMediaData[2]
                    vMediaTitle = vMediaData[4]
                    vMediaNoteHandles = vMediaData[8]
                    if(len(vMediaNoteHandles) > 0):
                        # Picture contains notes, then special treatment
                        self.__PictureWithNote(vSubLevel, vMediaPath, vMediaTitle, vMediaNoteHandles)

                        # Done, remove from list
                        vFilteredPhotoList.remove(vMediaHandle)

                #
                # 2. Remaining photos, side by side
                #
                vCounter = 0

                vTempList = vFilteredPhotoList.copy() # Use temporary list, so items can be removed while iterating
                for vMediaHandle in vTempList:
                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)
                    vCounter = vCounter + 1
                    if (vCounter % 2 == 1):
                        vMediaPath_1  = vMediaData[2]
                        vMediaTitle_1 = vMediaData[4]

                        # Remove media_1 from list
                        vFilteredPhotoList.remove(vMediaData[0])
                    else:
                        vMediaPath_2  = vMediaData[2]
                        vMediaTitle_2 = vMediaData[4]
                        hsf.PictureSideBySideEqualHeight(vSubLevel, vMediaPath_1, vMediaPath_2, vMediaTitle_1, vMediaTitle_2)

                        # Remove media_2 from list
                        vFilteredPhotoList.remove(vMediaData[0])

                        # Reset variables
                        vMediaPath_1  = None
                        vMediaTitle_1 = None

                        vMediaPath_2  = None
                        vMediaTitle_2 = None

                #
                # 3. In case temp list had an odd length, one document might be remaining
                #
                if(vMediaPath_1 is not None):
                    # One picture remaining
                    with vSubLevel.create(hlt.Figure(position='htpb')) as vPhoto:
                        vPhoto.add_image(pl.NoEscape(vMediaPath_1)) # TODO: Zoom in on vMediaRect
                        vPhoto.add_caption(pu.escape_latex(vMediaTitle_1))

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __WriteDocumentSection(self, pLevel):
        """
        Create section with document scans
        """

        vFilteredDocumentList = self.__GetFilteredDocumentList()
        if(len(vFilteredDocumentList) > 0):
            # Allocate variables
            vMediaPath_1  = None
            vMediaTitle_1 = None
            vMediaRect_1  = None
            vMediaPath_2  = None
            vMediaTitle_2 = None
            vMediaRect_2  = None

            # Debug
            #print("hkPersonChapter:__WriteDocumentSection - vFilteredDocumentList: ", vFilteredDocumentList)

            pLevel.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=pLevel, pTitle=hlg.Translate('documents', self.__language), pLabel=False) as vSubLevel:
                #
                # 1. All documents with notes
                #
                vTempList = vFilteredDocumentList.copy() # Use temporary list, so items can be removed while iterating
                for vItem in vTempList:
                    vMediaHandle = vItem[0]
                    vMediaRect   = vItem[1]

                    vMediaData        = GetMediaData(vMediaHandle, self.__Cursor)
                    vMediaPath        = vMediaData[2]
                    vMediaTitle       = vMediaData[4]
                    vMediaNoteHandles = self.__GetFilteredNoteList(vMediaData[8])

                    # TODO: dit gaat mis als het om een note met tag 'source' gaat
                    if(len(vMediaNoteHandles) > 0):
                        # Document contains notes, then treatment
                        self.__DocumentWithNote(vSubLevel, vMediaPath, vMediaTitle, vMediaNoteHandles, vMediaRect) #20220322: Added vMediaRect

                        # Done, remove from list
                        vFilteredDocumentList.remove(vItem)

                #
                # 2. Remaining documents, side by side
                #
                vCounter = 0

                vTempList = vFilteredDocumentList.copy() # Use temporary list, so items can be removed while iterating
                for vItem in vTempList:
                    vMediaHandle = vItem[0]
                    vMediaRect   = vItem[1]

                    vMediaData = GetMediaData(vMediaHandle, self.__Cursor)

                    vCounter = vCounter + 1
                    if (vCounter % 2 == 1):
                        vMediaPath_1  = vMediaData[2]
                        vMediaTitle_1 = vMediaData[4]
                        vMediaRect_1  = vMediaRect

                        # Remove media_1 from list
                        vFilteredDocumentList.remove(vItem)
                    else:
                        vMediaPath_2  = vMediaData[2]
                        vMediaTitle_2 = vMediaData[4]
                        vMediaRect_2 = vMediaRect

                        hsf.PictureSideBySideEqualHeight(vSubLevel, vMediaPath_1, vMediaPath_2, vMediaTitle_1, vMediaTitle_2, vMediaRect_1, vMediaRect_2) # 20220322: Added vMediaRect_1, vMediaRect_2

                        # Remove media_2 from list
                        vFilteredDocumentList.remove(vItem)

                        # Reset variables
                        vMediaPath_1  = None
                        vMediaTitle_1 = None
                        vMediaRect_1  = None

                        vMediaPath_2  = None
                        vMediaTitle_2 = None
                        vMediaRect_2  = None

                #
                # 3. In case temp list had an odd length, one document might be remaining
                #
                if(vMediaPath_1 is not None):
                    # One picture remaining
                    with vSubLevel.create(hlt.Figure(position='htpb')) as vPhoto:
                        vPhoto.add_image(pl.NoEscape(vMediaPath_1)) # TODO: Zoom in on vMediaRect
                        vPhoto.add_caption(pu.escape_latex(vMediaTitle_1))

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def WritePersonChapter(self):
        """
        Writes the person to a separate chapter in a subdocument
        """

        # Display progress
        print("Writing a chapter about: ", self.GivenNames, self.Surname)

        # Create a new chapter for the active person
        vChapter = hlt.Chapter(title=self.GivenNames + ' ' + self.Surname, label=self.GrampsId)

        self.__WriteLifeSketchSection(vChapter)
        self.__WriteVitalInformationSection(vChapter)
        #self.__WriteFamilySection(vChapter)
        self.__WriteParentalSection_Graph(vChapter)
        self.__WritePartnerSections_Graph(vChapter)

        self.__WriteEducationSection(vChapter)
        self.__WriteProfessionSection(vChapter)
        self.__WriteResidenceSection_Timeline(vChapter)
        #self.__WriteResidenceSection_Map(vChapter)
        self.__WritePhotoSection(vChapter)
        self.__WriteDocumentSection(vChapter)

        vChapter.generate_tex(filepath=self.DocumentPath + self.GrampsId)
