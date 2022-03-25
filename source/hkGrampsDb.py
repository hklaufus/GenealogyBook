import sqlite3
import pickle
import pathlib

# Niet zo chique hier...

# Constants
vGrampsPersonTable = 'person'
vGrampsFamilyTable = 'family'
vGrampsEventTable = 'event'
vGrampsMediaTable = 'media'

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py
vEventUnknown = -1
vEventCustom = 0
vEventMarriage = 1
vEventMarriageSettlement = 2
vEventMarriageLicense = 3
vEventMarriageContract = 4
vEventMarriageBanns = 5
vEventEngagement = 6
vEventDivorce = 7
vEventDivorceFiling = 8
vEventAnnulment = 9
vEventAlternateMarriage = 10
vEventAdopted = 11
vEventBirth = 12
vEventDeath = 13
vEventAdultChristening = 14
vEventBaptism = 15
vEventBarMitzvah = 16
vEventBasMitzvah = 17
vEventBlessing = 18
vEventBurial = 19
vEventCauseOfDeath = 20
vEventCensus = 21
vEventChristening = 22
vEventConfirmation = 23
vEventCremation = 24
vEventDegree = 25
vEventEducation = 26
vEventElected = 27
vEventEmigration = 28
vEventFirstCommunion = 29
vEventImmigration = 30
vEventGraduation = 31
vEventMedicalInformation = 32
vEventMilitaryService = 33
vEventNaturalization = 34
vEventNobilityTitle = 35
vEventNumberOfMarriages = 36
vEventOccupation = 37
vEventOrdination = 38
vEventProbate = 39
vEventProperty = 40
vEventReligion = 41
vEventResidence = 42
vEventRetirement = 43
vEventWill = 44

vVitalEventsSet = {
    vEventBirth,
    vEventBaptism,
    vEventChristening,
    vEventAdopted,
    vEventFirstCommunion,
    vEventBarMitzvah,
    vEventBasMitzvah,
    vEventBlessing,
    vEventAdultChristening,
    vEventConfirmation,
    vEventElected,
    vEventEmigration,
    vEventImmigration,
    vEventNaturalization,
    vEventNobilityTitle,
    vEventDeath,
    vEventBurial,
    vEventCremation,
    vEventWill}

vFamilyEventsSet = {
    vEventMarriage,
    vEventMarriageSettlement,
    vEventMarriageLicense,
    vEventMarriageContract,
    vEventMarriageBanns,
    vEventEngagement,
    vEventDivorce,
    vEventDivorceFiling,
    vEventAnnulment,
    vEventAlternateMarriage}

vEducationEventsSet = {
    vEventDegree, 
    vEventEducation, 
    vEventGraduation}

vProfessionalEventsSet = {
    vEventOccupation}  # , vEventRetirement}

vResidentialEventsSet = {
    vEventProperty, 
    vEventResidence}

vEventTypeDict = {
    vEventUnknown: "Unknown",
    vEventCustom: "Custom",
    vEventMarriage: "Marriage",
    vEventMarriageSettlement: "Marriage Settlement",
    vEventMarriageLicense: "Marriage License",
    vEventMarriageContract: "Marriage Contract",
    vEventMarriageBanns: "Marriage Banns",
    vEventEngagement: "Engagement",
    vEventDivorce: "Divorce",
    vEventDivorceFiling: "Divorce Filing",
    vEventAnnulment: "Annulment",
    vEventAlternateMarriage: "Alternate Marriage",
    vEventAdopted: "Adopted",
    vEventBirth: "Birth",
    vEventDeath: "Death",
    vEventAdultChristening: "Adult Christening",
    vEventBaptism: "Baptism",
    vEventBarMitzvah: "Bar Mitzvah",
    vEventBasMitzvah: "Bas Mitzvah",
    vEventBlessing: "Blessing",
    vEventBurial: "Burial",
    vEventCauseOfDeath: "Cause Of Death",
    vEventCensus: "Census",
    vEventChristening: "Christening",
    vEventConfirmation: "Confirmation",
    vEventCremation: "Cremation",
    vEventDegree: "Degree",
    vEventEducation: "Education",
    vEventElected: "Elected",
    vEventEmigration: "Emigration",
    vEventFirstCommunion: "First Communion",
    vEventImmigration: "Immigration",
    vEventGraduation: "Graduation",
    vEventMedicalInformation: "Medical Information",
    vEventMilitaryService: "Military Service",
    vEventNaturalization: "Naturalization",
    vEventNobilityTitle: "Nobility Title",
    vEventNumberOfMarriages: "Number of Marriages",
    vEventOccupation: "Occupation",
    vEventOrdination: "Ordination",
    vEventProbate: "Probate",
    vEventProperty: "Property",
    vEventReligion: "Religion",
    vEventResidence: "Residence",
    vEventRetirement: "Retirement",
    vEventWill: "Will"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/date.py
vDateModifierNone = 0
vDateModifierBefore = 1
vDateModifierAfter = 2
vDateModifierAbout = 3
vDateModifierRange = 4
vDateModifierSpan = 5
vDateModifierTextOnly = 6

vDateModifierDict = {
    vDateModifierNone: "None",
    vDateModifierBefore: "Before",
    vDateModifierAfter: "After",
    vDateModifierAbout: "About",
    vDateModifierRange: "Range",
    vDateModifierSpan: "Span",
    vDateModifierTextOnly: "Text Only"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/notetype.py
vNoteUnknown = -1
vNoteCustom = 0
vNoteGeneral = 1
vNoteResearch = 2
vNoteTranscript = 3
vNotePerson = 4
vNoteAttribute = 5
vNoteAddress = 6
vNoteAssociation = 7
vNoteLds = 8
vNoteFamily = 9
vNoteEvent = 10
vNoteEventref = 11
vNoteSource = 12
vNoteSourceref = 13
vNotePlace = 14
vNoteRepo = 15
vNoteReporef = 16
vNoteMedia = 17
vNoteMediaref = 18
vNoteChildref = 19
vNotePersonname = 20
vNoteSource_Text = 21
vNoteCitation = 22
vNoteReport_Text = 23
vNoteHtml_Code = 24
vNoteTodo = 25
vNoteLink = 26

vNoteTypeDict = {
    vNoteUnknown: "Unknown",
    vNoteCustom: "Custom",
    vNoteGeneral: "General",
    vNoteResearch: "Research",
    vNoteTranscript: "Transcript",
    vNotePerson: "Person",
    vNoteAttribute: "Attribute",
    vNoteAddress: "Address",
    vNoteAssociation: "Association",
    vNoteLds: "Lds",
    vNoteFamily: "Family",
    vNoteEvent: "Event",
    vNoteEventref: "Eventref",
    vNoteSource: "Source",
    vNoteSourceref: "Sourceref",
    vNotePlace: "Place",
    vNoteRepo: "Repo",
    vNoteReporef: "Reporef",
    vNoteMedia: "Media",
    vNoteMediaref: "Mediaref",
    vNoteChildref: "Childref",
    vNotePersonname: "Personname",
    vNoteSource_Text: "Source_Text",
    vNoteCitation: "Citation",
    vNoteReport_Text: "Report_Text",
    vNoteHtml_Code: "Html_Code",
    vNoteTodo: "Todo",
    vNoteLink: "Link"
}


# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/person.py
vGenderFemale = 0
vGenderMale = 1
vGenderUnknown = 2

vGenderDict = {
    vGenderFemale: "Female",
    vGenderMale: "Male",
    vGenderUnknown: "Unknown"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventroletype.py
vRoleUnknown = -1
vRoleCustom = 0
vRolePrimary = 1
vRoleClergy = 2
vRoleCelebrant = 3
vRoleAide = 4
vRoleBride = 5
vRoleGroom = 6
vRoleWitness = 7
vRoleFamily = 8
vRoleInformant = 9

vRoleDict = {
    vRoleUnknown: "Unknown",
    vRoleCustom: "Custom",
    vRolePrimary: "Primary",
    vRoleClergy: "Clergy",
    vRoleCelebrant: "Celebrant",
    vRoleAide: "Aide",
    vRoleBride: "Bride",
    vRoleGroom: "Groom",
    vRoleWitness: "Witness",
    vRoleFamily: "Family"
}

vPlaceTypeUnknown = -1
vPlaceTypeCustom = 0
vPlaceTypeCountry = 1
vPlaceTypeState = 2
vPlaceTypeCounty = 3
vPlaceTypeCity = 4
vPlaceTypeParish = 5
vPlaceTypeLocalty = 6
vPlaceTypeStreet = 7
vPlaceTypeProvince = 8
vPlaceTypeRegion = 9
vPlaceTypeDepartment = 10
vPlaceTypeNeighborhood = 11
vPlaceTypeDistrict = 12
vPlaceTypeBorough = 13
vPlaceTypeMunicipality = 14
vPlaceTypeTown = 15
vPlaceTypeVillage = 16
vPlaceTypeHamlet = 17
vPlaceTypeFarm = 18
vPlaceTypeBuilding = 19
vPlaceTypeNumber = 20

vPlaceTypeDict = {
    vPlaceTypeUnknown: "Unknown",
    vPlaceTypeCustom: "Custom",
    vPlaceTypeCountry: "Country",
    vPlaceTypeState: "State",
    vPlaceTypeCounty: "County",
    vPlaceTypeCity: "City",
    vPlaceTypeParish: "Parish",
    vPlaceTypeLocalty: "Localty",
    vPlaceTypeStreet: "Street",
    vPlaceTypeProvince: "Province",
    vPlaceTypeRegion: "Region",
    vPlaceTypeDepartment: "Department",
    vPlaceTypeNeighborhood: "Neighborhood",
    vPlaceTypeDistrict: "District",
    vPlaceTypeBorough: "Borough",
    vPlaceTypeMunicipality: "Municipality",
    vPlaceTypeTown: "Town",
    vPlaceTypeVillage: "Village",
    vPlaceTypeHamlet: "Hamlet",
    vPlaceTypeFarm: "Farm",
    vPlaceTypeBuilding: "Building",
    vPlaceTypeNumber: "Number"
}

def GetFamilyHandlesByParent(pParentHandle, pCursor):
    """
    Retrieves all family handles of which person is the parent
    """

    pCursor.execute(
        'SELECT handle FROM family WHERE father_handle=? OR mother_handle=?', [
            pParentHandle, pParentHandle])
    vFamilyHandles = pCursor.fetchall()

    return vFamilyHandles


def GetAllFamilyHandles(pPersonHandle, pCursor):
    """
    Retrieves all family handles of which person is the parent
    """

    pCursor.execute('SELECT DISTINCT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family"',[pPersonHandle])
    vFamilyHandles = pCursor.fetchall()

    return vFamilyHandles


def GetPartnerHandle(pPersonHandle, pFamilyHandle, pCursor):
    """
    Retrieves one partner of person
    """

    pCursor.execute('SELECT mother_handle FROM family WHERE father_handle=? AND handle=?', [pPersonHandle, pFamilyHandle])
    vPartnerHandle = pCursor.fetchone()

    # If zero length list is returned, pPersonHandle might be the mother
    # instead of the father
    if(vPartnerHandle is None):
        pCursor.execute(
            'SELECT father_handle FROM family WHERE mother_handle=? AND handle=?', [
                pPersonHandle, pFamilyHandle])
        vPartnerHandle = pCursor.fetchone()

    if(vPartnerHandle is not None):
        vPartnerHandle = vPartnerhandle[0]

    return vPartnerHandle


def GetPartnerHandles(pPersonHandle, pCursor):
    """
    Retreives all partners of person
    """

    pCursor.execute(
        'SELECT mother_handle FROM family WHERE father_handle=?',
        [pPersonHandle])
    vPartnerHandles1 = pCursor.fetchall()

    # If zero length list is returned, pPersonHandle might be the mother
    # instead of the father
    if(len(vPartnerHandles1) == 0):
        pCursor.execute(
            'SELECT father_handle FROM family WHERE mother_handle=?',
            [pPersonHandle])
        vPartnerHandles1 = pCursor.fetchall()

    # Debug
#	print('vPartnerHandles1: ', vPartnerHandles1)

    vPartnerHandles2 = []
    for vPartnerHandle in vPartnerHandles1:
        vPartnerHandles2.append(vPartnerHandle[0])

    return vPartnerHandles2


def GetFatherHandleByFamily(pFamilyHandle, pCursor):
    pCursor.execute(
        'SELECT father_handle FROM family WHERE handle=?',
        [pFamilyHandle])
    vFatherHandle = pCursor.fetchone()

    if(vFatherHandle is not None):
        vFatherHandle = vFatherHandle[0]

    return vFatherHandle


def GetMotherHandleByFamily(pFamilyHandle, pCursor):
    pCursor.execute(
        'SELECT mother_handle FROM family WHERE handle=?',
        [pFamilyHandle])
    vMotherHandle = pCursor.fetchone()

    if(vMotherHandle is not None):
        vMotherHandle = vMotherHandle[0]

    return vMotherHandle


def GetFatherHandleByPerson(pPersonHandle, pCursor):
    """
    Retrieves the father for the given person
    """

    vFatherHandle = None

#	pCursor.execute('SELECT father_handle, mother_handle FROM family WHERE handle IN (SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family") AND NOT father_handle=? AND NOT mother_handle=?', [pPersonHandle, pPersonHandle, pPersonHandle])
    pCursor.execute(
        'SELECT A.father_handle, A.mother_handle, A.handle, B.ref_handle, B.obj_handle, B.ref_class FROM family A, reference B WHERE COALESCE(A.father_handle,"")!=? AND COALESCE(A.mother_handle,"")!=? AND A.handle=B.ref_handle AND B.obj_handle=? AND B.ref_class="Family"', [
            pPersonHandle, pPersonHandle, pPersonHandle])
    vRecord = pCursor.fetchone()

    if(vRecord is not None):
        vFatherHandle = vRecord[0]

    return vFatherHandle


def GetMotherHandleByPerson(pPersonHandle, pCursor):
    """
    Retrieves the mother for the given person
    """

    vMotherHandle = None

#	pCursor.execute('SELECT father_handle, mother_handle FROM family WHERE handle IN (SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family") AND NOT father_handle=? AND NOT mother_handle=?', [pPersonHandle, pPersonHandle, pPersonHandle])
    pCursor.execute(
        'SELECT A.father_handle, A.mother_handle, A.handle, B.ref_handle, B.obj_handle, B.ref_class FROM family A, reference B WHERE COALESCE(A.father_handle,"")!=? AND COALESCE(A.mother_handle,"")!=? AND A.handle=B.ref_handle AND B.obj_handle=? AND B.ref_class="Family"', [
            pPersonHandle, pPersonHandle, pPersonHandle])
    vRecord = pCursor.fetchone()

    if(vRecord is not None):
        vMotherHandle = vRecord[1]

    return vMotherHandle


def GetFamilyHandleByFatherMother(pFatherHandle, pMotherHandle, pCursor):
    """
    Retrieves the family handle of the given father and mother
    """

    pCursor.execute(
        'SELECT handle FROM family WHERE (father_handle=? AND mother_handle=?)', [
            pFatherHandle, pMotherHandle])
    vFamilyHandle = pCursor.fetchone()

    return vFamilyHandle


def GetChildrenHandlesByPerson(pPersonHandle, pCursor):
    """
    Gets all children of a person, from multiple partners if applicable
    Returns a list
    """

    vChildrenHandles = []

    pCursor.execute(
        'SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND (obj_handle IN (SELECT father_handle FROM family WHERE handle=ref_handle) OR obj_handle IN (SELECT mother_handle FROM family WHERE handle=ref_handle))',
        [pPersonHandle])
    vFamilyHandles = pCursor.fetchall()

    for vFamilyHandle in vFamilyHandles:
        vChildrenHandles = vChildrenHandles + \
            GetChildrenHandlesByFamily(vFamilyHandle[0], pCursor)

    return vChildrenHandles


def GetChildrenHandlesByPerson_Old(pPersonHandle, pCursor):
    """
    Gets all children of a person, from multiple partners if applicable
    Returns a list
    """

    pCursor.execute(
        'SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND (obj_handle IN (SELECT father_handle FROM family WHERE handle=ref_handle) OR obj_handle IN (SELECT mother_handle FROM family WHERE handle=ref_handle))',
        [pPersonHandle])
    vFamilyHandles = pCursor.fetchall()

    vChildrenHandles = []
    for vFamilyHandle in vFamilyHandles:
        vChildrenHandles = vChildrenHandles + \
            GetChildrenHandlesByFamily(vFamilyHandle[0], pCursor)

    return vChildrenHandles


def GetChildrenHandlesByFamily(pFamilyHandle, pCursor):
    """
    Get all children of a family
    Returns a list
    """

    vChildrenHandles = []

    pCursor.execute(
        'SELECT handle, blob_data FROM family WHERE handle=?',
        [pFamilyHandle])
    vRecord = pCursor.fetchone()
    vBlobData = vRecord[1]
    vFamilyData = pickle.loads(vBlobData)
    vChildRefList = vFamilyData[4]

    for vChildRef in vChildRefList:
        vChildHandle = vChildRef[3]
        vChildrenHandles.append(vChildHandle)

    return vChildrenHandles


def GetChildrenHandlesByFamily_Old(pFamilyHandle, pCursor):
    """
    Get all children of a family
    Returns a list
    """

    pCursor.execute(
        'SELECT obj_handle FROM reference WHERE ref_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=?) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=?)', [
            pFamilyHandle, pFamilyHandle, pFamilyHandle])
    vChildrenHandles = pCursor.fetchall()

    vChildrenHandles2 = []
    for vChildHandle in vChildrenHandles:
        vChildrenHandles2.append(vChildHandle[0])

    return vChildrenHandles2


def GetSiblingHandles(pPersonHandle, pCursor):
    """
    Retrieves the siblings of the person.
    """

    # TODO: bug: also retrieves pPersonHandle as a sibling

    # Retrieve all family handles of which pPersonHandle is a member, but not
    # a father or a mother
    pCursor.execute(
        'SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)',
        [pPersonHandle])
    vFamilyHandles = pCursor.fetchall()

    vSiblingHandles = []
    for vFamilyHandle in vFamilyHandles:
        vSiblingHandles = vSiblingHandles + \
            GetChildrenHandlesByFamily(vFamilyHandle[0], pCursor)

    return vSiblingHandles


def GetSiblingHandles_Old(pPersonHandle, pCursor):
    """
    Retrieves the siblings of the person.
    """

    pCursor.execute(
        'SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)',
        [pPersonHandle])
    vFamilyHandle = pCursor.fetchone()

    vSiblingHandles2 = []
    if(vFamilyHandle is not None):
        vFamilyHandle = vFamilyHandle[0]

        pCursor.execute(
            'SELECT obj_handle FROM reference WHERE ref_handle=? AND ref_class="Family" AND obj_handle<>? AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)', [
                vFamilyHandle, pPersonHandle])
        vSiblingHandles = pCursor.fetchall()

        for vSiblingHandle in vSiblingHandles:
            vSiblingHandles2.append(vSiblingHandle[0])

    return vSiblingHandles2


def GetGrampsIdByPersonHandle(pPersonHandle, pCursor):
    pCursor.execute(
        'SELECT gramps_id FROM person WHERE handle=?',
        [pPersonHandle])
    vPersonId = pCursor.fetchone()

    if (vPersonId is not None):
        vPersonId = vPersonId[0]

    return vPersonId


def GetPersonHandleByGrampsId(pPersonId, pCursor):
    pCursor.execute('SELECT handle FROM person WHERE gramps_id=?', [pPersonId])
    vPersonHandle = pCursor.fetchone()

    if(vPersonHandle is not None):
        vPersonHandle = vPersonHandle[0]

    return vPersonHandle

def DecodeDateTuple(pDateTuple):
    vDay = ''
    vMonth = ''
    vYear = ''
    vDateList = []

    if(pDateTuple is not None):
        vModifier = pDateTuple[1]
        vDate = pDateTuple[3]

        if(len(vDate) == 4):
            # Single date
            [vDay, vMonth, vYear, _] = vDate
            vDateList = [vModifier, vDay, vMonth, vYear]

        elif(len(vDate) == 8):
            # Dual date
            [vDay1, vMonth1, vYear1, _, vDay2, vMonth2, vYear2, _] = vDate
            vDateList = [vModifier, vDay1, vMonth1, vYear1, vDay2, vMonth2, vYear2]

    return vDateList

def DecodeDateTuple_Old(pDateTuple):
    vDay = ''
    vMonth = ''
    vYear = ''
    vDateString = ''

    if(pDateTuple is None):
        vDateString = '-'
    else:
        vDate = pDateTuple[3]

        if(len(vDate) == 4):
            # Single date
            [vDay, vMonth, vYear, _] = vDate
            if(vDay == 0):
                vDay = ''

            if(vMonth == 0):
                vMonth = ''
            else:
                vMonth = calendar.month_name[vMonth][:3]

            vDateString = str(vDay) + ' ' + vMonth + ' ' + str(vYear)
            vDateString = vDateString.strip()

        elif(len(vDate) == 8):
            # Dual date
            [vDay1, vMonth1, vYear1, _, vDay2, vMonth2, vYear2, _] = vDate

            # Start date
            if(vDay1 == 0):
                vDay1 = ''

            if(vMonth1 == 0):
                vMonth1 = ''
            else:
                vMonth1 = calendar.month_name[vMonth1][:3]

            vDateString1 = str(vDay1) + ' ' + vMonth1 + ' ' + str(vYear1)
            vDateString1 = vDateString1.strip()

            # End date
            if(vDay2 == 0):
                vDay2 = ''

            if(vMonth2 == 0):
                vMonth2 = ''
            else:
                vMonth2 = calendar.month_name[vMonth2][:3]

            vDateString2 = str(vDay2) + ' ' + vMonth2 + ' ' + str(vYear2)
            vDateString2 = vDateString2.strip()

            vDateString = vDateString1 + ' - ' + vDateString2

        vModifier = pDateTuple[1]
        vModifierSet = {1, 2, 3}

        if(vModifier in vModifierSet):
            # Before, after, about
            vDateString = vDateModifierDict[vModifier] + ' ' + str(vDay) + ' ' + vMonth + ' ' + str(vYear)

        elif(vModifier == 4):
            # Range
            vDateString = 'Between ' + vDateString.split('-')[0] + ' and ' + vDateString.split('-')[1]

        elif(vModifier == 5):
            # Span
            #			vDateString = 'From ' + vDateString.split('-')[0] + ' until ' +  vDateString.split('-')[1]
            vDateString = vDateString.split('-')[0] + ' - ' + vDateString.split('-')[1]

#		else:
#			# Unknown modifier
#			print('ERROR in DecodeDateTuple: unknown modifier: ', vModifier, vDateModifierDict[vModifier])
#			print('pDateTuple: ', pDateTuple)

    return vDateString


def DecodePlaceData(pPlaceHandle, pCursor):
    # See https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/place.py
    vPlaceList = {}

    vPlaceHandle = pPlaceHandle
    while(len(vPlaceHandle) > 0):
        pCursor.execute('SELECT enclosed_by, blob_data FROM place WHERE handle=?', [vPlaceHandle])
        vRecord = pCursor.fetchone()
        if(vRecord is not None):
            vPlaceHandle = vRecord[0]
            vBlobData = vRecord[1]
            vPlaceData = pickle.loads(vBlobData)

            if(len(vPlaceData[3])==0):
                vLongitude = 0.
            else:
                vLongitude = float(vPlaceData[3])

            if(len(vPlaceData[4])==0):
                vLatitude = 0.
            else:
                vLatitude  = float(vPlaceData[4])

            vName = vPlaceData[6][0]
            vType = vPlaceTypeDict[vPlaceData[8][0]]
            vCode = vPlaceData[9]

            # Debug
#            print('vName     : ', vName)
#            print('vType     : ', vType)
#            print('vCode     : ', vCode)
#            print('vLatitude : ', vLatitude)
#            print('vLongitude: ', vLongitude)

            vPlaceList[vType] = [vName, (vLatitude, vLongitude), vCode]

    return vPlaceList

def DecodeEventData(pEventHandle, pCursor):
    vGrampsId = ""
    vType = ""
    vDate = ""
    vPlace = ""
    vDescription = ""
    vMediaList = []

    pCursor.execute('SELECT blob_data FROM event WHERE handle=?', [pEventHandle])
    vBlobData = pCursor.fetchone()
    if(vBlobData is not None):
        vEventData = pickle.loads(vBlobData[0])

        vGrampsId = vEventData[1]
        vType = vEventData[2]
        if(vType is not None):
            # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py
            vType = vType[0]

        vDate = vEventData[3]
        if(vDate is not None):
            vDate = DecodeDateTuple(vDate)
        else:
            vDate = '-'

        vDescription = vEventData[4]

        vPlaceHandle = vEventData[5]
        if(vPlaceHandle is not None):
            vPlace = DecodePlaceData(vPlaceHandle, pCursor)

        vMediaList = vEventData[8]

    return [vType, vDate, vPlace, vDescription, vMediaList]


def DecodeFamilyData(pFamilyHandle, pCursor):
    # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/family.py

    vGrampsId = ""
    vFatherHandle = ""
    vMotherHandle = ""
    vChildRefList = []
    vType = ""
    vEventRefList = []
    vMediaList = []

    pCursor.execute(
        'SELECT blob_data, gramps_id, father_handle, mother_handle FROM family WHERE handle=?',
        [pFamilyHandle])
    vRecord = pCursor.fetchone()

    if(vRecord is not None):
        vBlobData = vRecord[0]
        vGrampsId = vRecord[1]
        vFatherHandle = vRecord[2]
        vMotherHandle = vRecord[3]

        if(vBlobData is not None):
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#2._Family:
            vFamilyData = pickle.loads(vBlobData)

            vGrampsId = vFamilyData[1]
            vFatherHandle = vFamilyData[2]
            vMotherHandle = vFamilyData[3]
            vChildRefList = vFamilyData[4]
            vType = vFamilyData[5]
            vEventRefList = vFamilyData[6]
            vMediaList = vFamilyData[7]

    return [
        vGrampsId,
        vFatherHandle,
        vMotherHandle,
        vChildRefList,
        vType,
        vEventRefList,
        vMediaList]


def DecodePersonData(pPersonHandle, pCursor):
    vGivenName = ""
    vSurname = ""
    vCallName = ""

    vPersonData = []

    vHandle = ""
    vGrampsId = ""
    vGender = 2
    vPrimaryName = []
    vAlternateName = []
    vDeathRefIndex = -1
    vBirthRefIndex = -1
    vEventRefList = []
    vFamilyList = []
    vParentFamilyList = []
    vMediaBase = []
    vAddressBase = []
    vAttributeBase = []
    vUrlBase = []
    vLdsOrdBase = []
    vCitationBase = []
    vNoteBase = []
    vChange = 0
    vTagBase = []
    vPrivate = False
    vPersonRefList = []

    pCursor.execute(
        'SELECT given_name, surname, blob_data FROM person WHERE handle=?',
        [pPersonHandle])
    vRecord = pCursor.fetchone()

    # Debug
#	print('vRecord: ', vRecord)

    if(vRecord is not None):
        vGivenName = vRecord[0]
        vSurname = vRecord[1]
        vBlobData = vRecord[2]

        if(vBlobData is not None):
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#1._Person
            vPersonData = pickle.loads(vBlobData)
            vPersonData = list(vPersonData)

            # Debug
#			print('vPersonData: ', vPersonData)

            vHandle = vPersonData[0]
            vGrampsId = vPersonData[1]
            vGender = vPersonData[2]
            vPrimaryName = vPersonData[3]
            vAlternateName = vPersonData[4]
            vDeathRefIndex = vPersonData[5]
            vBirthRefIndex = vPersonData[6]
            vEventRefList = vPersonData[7]
            vFamilyList = vPersonData[8]
            vParentFamilyList = vPersonData[9]
            vMediaBase = vPersonData[10]
            vAddressBase = vPersonData[11]
            vAttributeBase = vPersonData[12]
            vUrlBase = vPersonData[13]
            vLdsOrdBase = vPersonData[14]
            vCitationBase = vPersonData[15]
            vNoteBase = vPersonData[16]
            vChange = vPersonData[17]
            vTagBase = vPersonData[18]
            vPrivate = vPersonData[19]
            vPersonRefList = vPersonData[20]

            vCallName = vPrimaryName[12]
            vGivenName = vPrimaryName[4]
            vSurname = vPrimaryName[5][0][1] + ' ' + vPrimaryName[5][0][0]

            vPersonData[3] = [
                vSurname.strip(),
                vGivenName.strip(),
                vCallName.strip()]  # Overwrite primary names

    return vPersonData


def GetPersonNotesHandles(pPersonHandle, pCursor):
    pCursor.execute(
        'SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Note"',
        [pPersonHandle])
    vNotesHandles = pCursor.fetchall()

    return vNotesHandles


def DecodeNoteData(pNoteHandle, pCursor):
    vHandle = ""
    vGrampsId = ""
    vText = []
    vFormat = ""
    vType = []
    vChange = 0
    vTagBase = []
    vPrivate = False

    vNoteData = []

    pCursor.execute('SELECT blob_data FROM note WHERE handle=?', [pNoteHandle])
    vRecord = pCursor.fetchone()

    if(vRecord is not None):
        vBlobData = vRecord[0]

        if(vBlobData is not None):
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#9._Note
            vNoteData = pickle.loads(vBlobData)

            # Debug
#			print('vNoteData: ', vNoteData)

            vHandle = vNoteData[0]
            vGrampsId = vNoteData[1]
            vText = vNoteData[2][0]
            vFormat = vNoteData[3]
            vType = vNoteData[4][0]
            vChange = vNoteData[5]
            vTagBase = vNoteData[6]
            vPrivate = vNoteData[7]

            # Debug
#			print('vNoteData: ', vNoteData)
#			print('vNoteText: ', vNoteText)
#			print('vNoteType: ', vNoteType)

    return vNoteData


def GetMediaData(pMediaHandle, pCursor):
    vHandle = ""
    vGrampsId = ""
    vPath = ""
    vMime = ""
    vDescription = ""
    vCheckSum = ""
    vAttributeBase = []
    vCitationBase = []
    vNoteBase = []
    vChange = 0
    vDataBase = ()
    vTagBase = []
    vPrivate = False

    vMediaData = []

    vBasePath = ""

    # Get base media path
    pCursor.execute('SELECT value FROM metadata WHERE setting=?', ['media-path'])
    vBlobData = pCursor.fetchone()

    if(vBlobData is not None):
        vBasePath = pickle.loads(vBlobData[0])

        # Get path for pMediaHandle
        pCursor.execute('SELECT blob_data FROM media WHERE handle=?', [pMediaHandle])
        vRecord = pCursor.fetchone()

        if(vRecord is not None):
            vMediaData = pickle.loads(vRecord[0])
            vMediaData = list(vMediaData)

            vHandle = vMediaData[0]
            vGrampsId = vMediaData[1]
            vPath = vMediaData[2]
            vMime = vMediaData[3]
            vDescription = vMediaData[4]
            vCheckSum = vMediaData[5]
            vAttributeBase = vMediaData[6]
            vCitationBase = vMediaData[7]
            vNoteBase = vMediaData[8]
            vChange = vMediaData[9]
            vDataBase = vMediaData[10]
            vTagBase = vMediaData[11]
            vPrivate = vMediaData[12]

            # Debug
#            if(vGrampsId == "O0008"):
#                print("vMediaData: ", vMediaData)

            # Check whether path is relative or absolute
            vPathObject = pathlib.Path(vPath)
            if(not vPathObject.is_absolute()):
                # Relative path, add base path
                vPathObject = pathlib.Path.joinpath(pathlib.Path(vBasePath), vPathObject)

            vMediaData[2] = str(vPathObject.as_posix())

    return vMediaData


def GetTagDictionary(pCursor):
    vTagDictionary = {}

    pCursor.execute('SELECT handle, name FROM tag')
    vTagData = pCursor.fetchall()

    for vTag in vTagData:
        vTagDictionary[vTag[0]] = vTag[1]

    # Debug
#	print("vTagDictionary: ", vTagDictionary)

    return vTagDictionary


def GetTagList(pTagHandleList, pTagDictionary):
    vTagList = []

    for vTagHandle in pTagHandleList:
        vTagList.append(pTagDictionary[vTagHandle])

    # Debug
#	print("vTagList: ", vTagList)

    return vTagList
