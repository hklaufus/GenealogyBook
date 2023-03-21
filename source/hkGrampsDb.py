import calendar
# import sqlite3
import logging
import pickle
import pathlib
# from typing import List, Any

# Niet zo chique hier...

# Constants
c_gramps_person_table: str = 'person'
c_gramps_family_table: str = 'family'
c_gramps_event_table: str = 'event'
c_gramps_media_table: str = 'media'

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py
c_event_unknown: int = -1
c_event_custom: int = 0
c_event_marriage: int = 1
c_event_marriage_settlement: int = 2
c_event_marriage_license: int = 3
c_event_marriage_contract: int = 4
c_event_marriage_banns: int = 5
c_event_engagement: int = 6
c_event_divorce: int = 7
c_event_divorce_filing: int = 8
c_event_annulment: int = 9
c_event_alternate_marriage: int = 10
c_event_adopted: int = 11
c_event_birth: int = 12
c_event_death: int = 13
c_event_adult_christening: int = 14
c_event_baptism: int = 15
c_event_bar_mitzvah: int = 16
c_event_bas_mitzvah: int = 17
c_event_blessing: int = 18
c_event_burial: int = 19
c_event_cause_of_death: int = 20
c_event_census: int = 21
c_event_christening: int = 22
c_event_confirmation: int = 23
c_event_cremation: int = 24
c_event_degree: int = 25
c_event_education: int = 26
c_event_elected: int = 27
c_event_emigration: int = 28
c_event_first_communion: int = 29
c_event_immigration: int = 30
c_event_graduation: int = 31
c_event_medical_information: int = 32
c_event_military_service: int = 33
c_event_naturalization: int = 34
c_event_nobility_title: int = 35
c_event_number_of_marriages: int = 36
c_event_occupation: int = 37
c_event_ordination: int = 38
c_event_probate: int = 39
c_event_property: int = 40
c_event_religion: int = 41
c_event_residence: int = 42
c_event_retirement: int = 43
c_event_will: int = 44

c_vital_events_set = {
    c_event_birth,
    c_event_baptism,
    c_event_christening,
    c_event_adopted,
    c_event_first_communion,
    c_event_bar_mitzvah,
    c_event_bas_mitzvah,
    c_event_blessing,
    c_event_adult_christening,
    c_event_confirmation,
    c_event_elected,
    c_event_emigration,
    c_event_immigration,
    c_event_naturalization,
    c_event_nobility_title,
    c_event_death,
    c_event_burial,
    c_event_cremation,
    c_event_will}

c_family_events_set = {
    c_event_marriage,
    c_event_marriage_settlement,
    c_event_marriage_license,
    c_event_marriage_contract,
    c_event_marriage_banns,
    c_event_engagement,
    c_event_divorce,
    c_event_divorce_filing,
    c_event_annulment,
    c_event_alternate_marriage}

c_education_events_set = {
    c_event_degree,
    c_event_education,
    c_event_graduation}

c_professional_events_set = {
    c_event_occupation}  # , c_event_retirement}

c_residential_events_set = {
    c_event_property,
    c_event_residence}

c_event_type_dict = {
    c_event_unknown: "Unknown",
    c_event_custom: "Custom",
    c_event_marriage: "Marriage",
    c_event_marriage_settlement: "Marriage Settlement",
    c_event_marriage_license: "Marriage License",
    c_event_marriage_contract: "Marriage Contract",
    c_event_marriage_banns: "Marriage Banns",
    c_event_engagement: "Engagement",
    c_event_divorce: "Divorce",
    c_event_divorce_filing: "Divorce Filing",
    c_event_annulment: "Annulment",
    c_event_alternate_marriage: "Alternate Marriage",
    c_event_adopted: "Adopted",
    c_event_birth: "Birth",
    c_event_death: "Death",
    c_event_adult_christening: "Adult Christening",
    c_event_baptism: "Baptism",
    c_event_bar_mitzvah: "Bar Mitzvah",
    c_event_bas_mitzvah: "Bas Mitzvah",
    c_event_blessing: "Blessing",
    c_event_burial: "Burial",
    c_event_cause_of_death: "Cause Of Death",
    c_event_census: "Census",
    c_event_christening: "Christening",
    c_event_confirmation: "Confirmation",
    c_event_cremation: "Cremation",
    c_event_degree: "Degree",
    c_event_education: "Education",
    c_event_elected: "Elected",
    c_event_emigration: "Emigration",
    c_event_first_communion: "First Communion",
    c_event_immigration: "Immigration",
    c_event_graduation: "Graduation",
    c_event_medical_information: "Medical Information",
    c_event_military_service: "Military Service",
    c_event_naturalization: "Naturalization",
    c_event_nobility_title: "Nobility Title",
    c_event_number_of_marriages: "Number of Marriages",
    c_event_occupation: "Occupation",
    c_event_ordination: "Ordination",
    c_event_probate: "Probate",
    c_event_property: "Property",
    c_event_religion: "Religion",
    c_event_residence: "Residence",
    c_event_retirement: "Retirement",
    c_event_will: "Will"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/date.py
c_date_modifier_none: int = 0
c_date_modifier_before: int = 1
c_date_modifier_after: int = 2
c_date_modifier_about: int = 3
c_date_modifier_range: int = 4
c_date_modifier_span: int = 5
c_date_modifier_text_only: int = 6

c_date_modifier_dict = {
    c_date_modifier_none: "None",
    c_date_modifier_before: "Before",
    c_date_modifier_after: "After",
    c_date_modifier_about: "About",
    c_date_modifier_range: "Range",
    c_date_modifier_span: "Span",
    c_date_modifier_text_only: "Text Only"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/notetype.py
c_note_unknown: int = -1
c_note_custom: int = 0
c_note_general: int = 1
c_note_research: int = 2
c_note_transcript: int = 3
c_note_person: int = 4
c_note_attribute: int = 5
c_note_address: int = 6
c_note_association: int = 7
c_note_lds: int = 8
c_note_family: int = 9
c_note_event: int = 10
c_note_event_ref: int = 11
c_note_source: int = 12
c_note_source_ref: int = 13
c_note_place: int = 14
c_note_repo: int = 15
c_note_repo_ref: int = 16
c_note_media: int = 17
c_note_media_ref: int = 18
c_note_child_ref: int = 19
c_note_person_name: int = 20
c_note_source_text: int = 21
c_note_citation: int = 22
c_note_report_text: int = 23
c_note_html_code: int = 24
c_note_todo: int = 25
c_note_link: int = 26

c_note_type_dict = {
    c_note_unknown: "Unknown",
    c_note_custom: "Custom",
    c_note_general: "General",
    c_note_research: "Research",
    c_note_transcript: "Transcript",
    c_note_person: "Person",
    c_note_attribute: "Attribute",
    c_note_address: "Address",
    c_note_association: "Association",
    c_note_lds: "Lds",
    c_note_family: "Family",
    c_note_event: "Event",
    c_note_event_ref: "Eventref",
    c_note_source: "Source",
    c_note_source_ref: "Sourceref",
    c_note_place: "Place",
    c_note_repo: "Repo",
    c_note_repo_ref: "Reporef",
    c_note_media: "Media",
    c_note_media_ref: "Mediaref",
    c_note_child_ref: "Childref",
    c_note_person_name: "Personname",
    c_note_source_text: "Source_Text",
    c_note_citation: "Citation",
    c_note_report_text: "Report_Text",
    c_note_html_code: "Html_Code",
    c_note_todo: "Todo",
    c_note_link: "Link"
}


# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/person.py
c_gender_female: int = 0
c_gender_male: int = 1
c_gender_unknown: int = 2

c_gender_dict = {
    c_gender_female: "Female",
    c_gender_male: "Male",
    c_gender_unknown: "Unknown"
}

# https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventroletype.py
c_role_unknown: int = -1
c_role_custom: int = 0
c_role_primary: int = 1
c_role_clergy: int = 2
c_role_celebrant: int = 3
c_role_aide: int = 4
c_role_bride: int = 5
c_role_groom: int = 6
c_role_witness: int = 7
c_role_family: int = 8
c_role_informant: int = 9

c_role_dict = {
    c_role_unknown: "Unknown",
    c_role_custom: "Custom",
    c_role_primary: "Primary",
    c_role_clergy: "Clergy",
    c_role_celebrant: "Celebrant",
    c_role_aide: "Aide",
    c_role_bride: "Bride",
    c_role_groom: "Groom",
    c_role_witness: "Witness",
    c_role_family: "Family"
}

c_place_type_unknown: int = -1
c_place_type_custom: int = 0
c_place_type_country: int = 1
c_place_type_state: int = 2
c_place_type_county: int = 3
c_place_type_city: int = 4
c_place_type_parish: int = 5
c_place_type_locality: int = 6
c_place_type_street: int = 7
c_place_type_province: int = 8
c_place_type_region: int = 9
c_place_type_department: int = 10
c_place_type_neighborhood: int = 11
c_place_type_district: int = 12
c_place_type_borough: int = 13
c_place_type_municipality: int = 14
c_place_type_town: int = 15
c_place_type_village: int = 16
c_place_type_hamlet: int = 17
c_place_type_farm: int = 18
c_place_type_building: int = 19
c_place_type_number: int = 20

c_place_type_dict = {
    c_place_type_unknown: "Unknown",
    c_place_type_custom: "Custom",
    c_place_type_country: "Country",
    c_place_type_state: "State",
    c_place_type_county: "County",
    c_place_type_city: "City",
    c_place_type_parish: "Parish",
    c_place_type_locality: "Locality",
    c_place_type_street: "Street",
    c_place_type_province: "Province",
    c_place_type_region: "Region",
    c_place_type_department: "Department",
    c_place_type_neighborhood: "Neighborhood",
    c_place_type_district: "District",
    c_place_type_borough: "Borough",
    c_place_type_municipality: "Municipality",
    c_place_type_town: "Town",
    c_place_type_village: "Village",
    c_place_type_hamlet: "Hamlet",
    c_place_type_farm: "Farm",
    c_place_type_building: "Building",
    c_place_type_number: "Number"
}


def get_family_handles_by_parent(p_parent_handle, p_cursor):
    """
    Retrieves all family handles of which person is the parent
    """

    p_cursor.execute(
        'SELECT handle FROM family WHERE father_handle=? OR mother_handle=?', [
            p_parent_handle, p_parent_handle])
    v_family_handles = p_cursor.fetchall()

    return v_family_handles


def get_all_family_handles(p_person_handle, p_cursor):
    """
    Retrieves all family handles of which person is the parent
    """

    p_cursor.execute('SELECT DISTINCT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family"', [p_person_handle])
    v_family_handles = p_cursor.fetchall()

    return v_family_handles


def get_partner_handle(p_person_handle, p_family_handle, p_cursor):
    """
    Retrieves one partner of person
    """

    p_cursor.execute('SELECT mother_handle FROM family WHERE father_handle=? AND handle=?', [p_person_handle, p_family_handle])
    v_partner_handle = p_cursor.fetchone()

    # If zero length list is returned, p_person_handle might be the mother
    # instead of the father
    if v_partner_handle is None:
        p_cursor.execute(
            'SELECT father_handle FROM family WHERE mother_handle=? AND handle=?', [
                p_person_handle, p_family_handle])
        v_partner_handle = p_cursor.fetchone()

    if v_partner_handle is not None:
        v_partner_handle = v_partner_handle[0]

    return v_partner_handle


def get_partner_handles(p_person_handle, p_cursor):
    """
    Retrieves all partners of person
    """

    p_cursor.execute('SELECT mother_handle FROM family WHERE father_handle=?', [p_person_handle])
    v_partner_handles_1 = p_cursor.fetchall()

    # If zero length list is returned, p_person_handle might be the mother
    # instead of the father
    if len(v_partner_handles_1) == 0:
        p_cursor.execute('SELECT father_handle FROM family WHERE mother_handle=?', [p_person_handle])
        v_partner_handles_1 = p_cursor.fetchall()

    # Debug
    # logging.debug('v_partner_handles_1: %s', v_partner_handles_1)

    v_partner_handles_2 = []
    for v_partner_handle in v_partner_handles_1:
        v_partner_handles_2.append(v_partner_handle[0])

    return v_partner_handles_2


def get_father_handle_by_family(p_family_handle, p_cursor):
    p_cursor.execute('SELECT father_handle FROM family WHERE handle=?', [p_family_handle])
    v_father_handle = p_cursor.fetchone()

    if v_father_handle is not None:
        v_father_handle = v_father_handle[0]

    return v_father_handle


def get_mother_handle_by_family(p_family_handle, p_cursor):
    p_cursor.execute('SELECT mother_handle FROM family WHERE handle=?', [p_family_handle])
    v_mother_handle = p_cursor.fetchone()

    if v_mother_handle is not None:
        v_mother_handle = v_mother_handle[0]

    return v_mother_handle


def get_father_handle_by_person(p_person_handle, p_cursor):
    """
    Retrieves the father for the given person
    """

    v_father_handle = None

    # p_cursor.execute('SELECT father_handle, mother_handle FROM family WHERE handle IN (SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family") AND NOT father_handle=? AND NOT mother_handle=?', [p_person_handle, p_person_handle, p_person_handle])
    p_cursor.execute('SELECT A.father_handle, A.mother_handle, A.handle, B.ref_handle, B.obj_handle, B.ref_class FROM family A, reference B WHERE COALESCE(A.father_handle,"")!=? AND COALESCE(A.mother_handle,"")!=? AND A.handle=B.ref_handle AND B.obj_handle=? AND B.ref_class="Family"', [p_person_handle, p_person_handle, p_person_handle])
    v_record = p_cursor.fetchone()

    if v_record is not None:
        v_father_handle = v_record[0]

    return v_father_handle


def get_mother_handle_by_person(p_person_handle, p_cursor):
    """
    Retrieves the mother for the given person
    """

    v_mother_handle = None

    # p_cursor.execute('SELECT father_handle, mother_handle FROM family WHERE handle IN (SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Family") AND NOT father_handle=? AND NOT mother_handle=?', [p_person_handle, p_person_handle, p_person_handle])
    p_cursor.execute('SELECT A.father_handle, A.mother_handle, A.handle, B.ref_handle, B.obj_handle, B.ref_class FROM family A, reference B WHERE COALESCE(A.father_handle,"")!=? AND COALESCE(A.mother_handle,"")!=? AND A.handle=B.ref_handle AND B.obj_handle=? AND B.ref_class="Family"', [p_person_handle, p_person_handle, p_person_handle])
    v_record = p_cursor.fetchone()

    if v_record is not None:
        v_mother_handle = v_record[1]

    return v_mother_handle


def get_family_handle_by_father_mother(p_father_handle, p_mother_handle, p_cursor):
    """
    Retrieves the family handle of the given father and mother
    """

    p_cursor.execute('SELECT handle FROM family WHERE (father_handle=? AND mother_handle=?)', [p_father_handle, p_mother_handle])
    v_family_handle = p_cursor.fetchone()

    return v_family_handle


def get_children_handles_by_person(p_person_handle, p_cursor):
    """
    Gets all children of a person, from multiple partners if applicable
    Returns a list
    """

    v_children_handles = []

    p_cursor.execute('SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND (obj_handle IN (SELECT father_handle FROM family WHERE handle=ref_handle) OR obj_handle IN (SELECT mother_handle FROM family WHERE handle=ref_handle))', [p_person_handle])
    v_family_handles = p_cursor.fetchall()

    for v_family_handle in v_family_handles:
        v_children_handles = v_children_handles + get_children_handles_by_family(v_family_handle[0], p_cursor)

    return v_children_handles


def get_children_handles_by_person_old(p_person_handle, p_cursor):
    """
    Gets all children of a person, from multiple partners if applicable
    Returns a list
    """

    p_cursor.execute('SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND (obj_handle IN (SELECT father_handle FROM family WHERE handle=ref_handle) OR obj_handle IN (SELECT mother_handle FROM family WHERE handle=ref_handle))', [p_person_handle])
    v_family_handles = p_cursor.fetchall()

    v_children_handles = []
    for v_family_handle in v_family_handles:
        v_children_handles = v_children_handles + \
                             get_children_handles_by_family(v_family_handle[0], p_cursor)

    return v_children_handles


def get_children_handles_by_family(p_family_handle, p_cursor):
    """
    Get all children of a family
    Returns a list
    """

    v_children_handles = []

    p_cursor.execute('SELECT handle, blob_data FROM family WHERE handle=?', [p_family_handle])
    v_record = p_cursor.fetchone()
    v_blob_data = v_record[1]
    v_family_data = pickle.loads(v_blob_data)
    v_child_ref_list = v_family_data[4]

    for v_child_ref in v_child_ref_list:
        v_child_handle = v_child_ref[3]
        v_children_handles.append(v_child_handle)

    return v_children_handles


def get_children_handles_by_family_old(p_family_handle, p_cursor):
    """
    Get all children of a family
    Returns a list
    """

    p_cursor.execute('SELECT obj_handle FROM reference WHERE ref_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=?) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=?)', [p_family_handle, p_family_handle, p_family_handle])
    v_children_handles = p_cursor.fetchall()

    v_children_handles2 = []
    for v_child_handle in v_children_handles:
        v_children_handles2.append(v_child_handle[0])

    return v_children_handles2


def get_sibling_handles(p_person_handle, p_cursor):
    """
    Retrieves the siblings of the person.
    """

    # TODO: bug: also retrieves p_person_handle as a sibling

    # Retrieve all family handles of which p_person_handle is a member, but not
    # a father or a mother
    p_cursor.execute('SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)', [p_person_handle])
    v_family_handles = p_cursor.fetchall()

    v_sibling_handles = []
    for vFamilyHandle in v_family_handles:
        v_sibling_handles = v_sibling_handles + get_children_handles_by_family(vFamilyHandle[0], p_cursor)

    return v_sibling_handles


def get_sibling_handles_old(p_person_handle, p_cursor):
    """
    Retrieves the siblings of the person.
    """

    p_cursor.execute('SELECT ref_handle, obj_handle FROM reference WHERE obj_handle=? AND ref_class="Family" AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)', [p_person_handle])
    v_family_handle = p_cursor.fetchone()

    v_sibling_handles2 = []
    if v_family_handle is not None:
        v_family_handle = v_family_handle[0]

        p_cursor.execute('SELECT obj_handle FROM reference WHERE ref_handle=? AND ref_class="Family" AND obj_handle<>? AND obj_handle NOT IN (SELECT father_handle FROM family WHERE handle=ref_handle) AND obj_handle NOT IN (SELECT mother_handle FROM family WHERE handle=ref_handle)', [v_family_handle, p_person_handle])
        v_sibling_handles = p_cursor.fetchall()

        for v_sibling_handle in v_sibling_handles:
            v_sibling_handles2.append(v_sibling_handle[0])

    return v_sibling_handles2


def get_gramps_id_by_person_handle(p_person_handle, p_cursor):
    p_cursor.execute('SELECT gramps_id FROM person WHERE handle=?', [p_person_handle])
    v_person_id = p_cursor.fetchone()

    if v_person_id is not None:
        v_person_id = v_person_id[0]

    return v_person_id


def get_person_handle_by_gramps_id(p_person_id, p_cursor):
    p_cursor.execute('SELECT handle FROM person WHERE gramps_id=?', [p_person_id])
    v_person_handle = p_cursor.fetchone()

    if v_person_handle is not None:
        v_person_handle = v_person_handle[0]

    return v_person_handle


def decode_date_tuple(p_date_tuple):
    v_date_list = []

    if p_date_tuple is not None:
        v_modifier = p_date_tuple[1]
        v_date = p_date_tuple[3]

        if len(v_date) == 4:
            # Single date
            [v_day, v_month, v_year, _] = v_date
            v_date_list = [v_modifier, v_day, v_month, v_year]

        elif len(v_date) == 8:
            # Dual date
            [v_day1, v_month1, v_year1, _, v_day2, v_month2, v_year2, _] = v_date
            v_date_list = [v_modifier, v_day1, v_month1, v_year1, v_day2, v_month2, v_year2]

    return v_date_list


def decode_date_tuple_old(p_date_tuple):
    v_day = ''
    v_month = ''
    v_year = ''
    v_date_string = ''

    if p_date_tuple is None:
        v_date_string = '-'
    else:
        v_date = p_date_tuple[3]

        if len(v_date) == 4:
            # Single date
            [v_day, v_month, v_year, _] = v_date
            if v_day == 0:
                v_day = ''

            if v_month == 0:
                v_month = ''
            else:
                v_month = calendar.month_name[v_month][:3]

            v_date_string = str(v_day) + ' ' + v_month + ' ' + str(v_year)
            v_date_string = v_date_string.strip()

        elif len(v_date) == 8:
            # Dual date
            [v_day1, v_month1, v_year1, _, v_day2, v_month2, v_year2, _] = v_date

            # Start date
            if v_day1 == 0:
                v_day1 = ''

            if v_month1 == 0:
                v_month1 = ''
            else:
                v_month1 = calendar.month_name[v_month1][:3]

            v_date_string1 = str(v_day1) + ' ' + v_month1 + ' ' + str(v_year1)
            v_date_string1 = v_date_string1.strip()

            # End date
            if v_day2 == 0:
                v_day2 = ''

            if v_month2 == 0:
                v_month2 = ''
            else:
                v_month2 = calendar.month_name[v_month2][:3]

            v_date_string2 = str(v_day2) + ' ' + v_month2 + ' ' + str(v_year2)
            v_date_string2 = v_date_string2.strip()

            v_date_string = v_date_string1 + ' - ' + v_date_string2

        v_modifier = p_date_tuple[1]
        v_modifier_set = {1, 2, 3}

        if v_modifier in v_modifier_set:
            # Before, after, about
            v_date_string = c_date_modifier_dict[v_modifier] + ' ' + str(v_day) + ' ' + v_month + ' ' + str(v_year)

        elif v_modifier == 4:
            # Range
            v_date_string = 'Between ' + v_date_string.split('-')[0] + ' and ' + v_date_string.split('-')[1]

        elif v_modifier == 5:
            # Span
            # vDateString = 'From ' + vDateString.split('-')[0] + ' until ' +  vDateString.split('-')[1]
            v_date_string = v_date_string.split('-')[0] + ' - ' + v_date_string.split('-')[1]

        # else:
        # 	# Unknown modifier
        # 	print('ERROR in DecodeDateTuple: unknown modifier: ', v_modifier, vDateModifierDict[v_modifier])
        # 	print('p_date_tuple: ', p_date_tuple)

    return v_date_string


def decode_place_data(p_place_handle, p_cursor):
    # See https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/place.py
    v_place_list = {}

    v_place_handle = p_place_handle
    while len(v_place_handle) > 0:
        p_cursor.execute('SELECT enclosed_by, blob_data FROM place WHERE handle=?', [v_place_handle])
        v_record = p_cursor.fetchone()
        if v_record is not None:
            v_place_handle = v_record[0]
            v_blob_data = v_record[1]
            v_place_data = pickle.loads(v_blob_data)

            if len(v_place_data[3]) == 0:
                v_longitude = 0.
            else:
                v_longitude = float(v_place_data[3])

            if len(v_place_data[4]) == 0:
                v_latitude = 0.
            else:
                v_latitude = float(v_place_data[4])

            v_name = v_place_data[6][0]
            v_type = c_place_type_dict[v_place_data[8][0]]
            v_code = v_place_data[9]

            # Debug
#            print('v_name     : ', v_name)
#            print('v_type     : ', v_type)
#            print('v_code     : ', v_code)
#            print('v_latitude : ', v_latitude)
#            print('v_longitude: ', v_longitude)

            v_place_list[v_type] = [v_name, (v_latitude, v_longitude), v_code]

    return v_place_list


def decode_event_data(p_event_handle, p_cursor):
    v_type = ""
    v_date = ""
    v_place = ""
    v_description = ""
    v_media_list = []

    p_cursor.execute('SELECT blob_data FROM event WHERE handle=?', [p_event_handle])
    v_blob_data = p_cursor.fetchone()
    if v_blob_data is not None:
        v_event_data = pickle.loads(v_blob_data[0])

        v_type = v_event_data[2]
        if v_type is not None:
            # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py
            v_type = v_type[0]

        v_date = v_event_data[3]
        if v_date is not None:
            v_date = decode_date_tuple(v_date)
        else:
            v_date = '-'

        v_description = v_event_data[4]

        v_place_handle = v_event_data[5]
        if v_place_handle is not None:
            v_place = decode_place_data(v_place_handle, p_cursor)

        v_media_list = v_event_data[8]

    return [v_type, v_date, v_place, v_description, v_media_list]


def decode_family_data(p_family_handle, p_cursor):
    # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/family.py

    v_gramps_id = ""
    v_father_handle = ""
    v_mother_handle = ""
    v_child_ref_list = []
    v_type = ""
    v_event_ref_list = []
    v_media_list = []

    p_cursor.execute('SELECT blob_data, gramps_id, father_handle, mother_handle FROM family WHERE handle=?', [p_family_handle])
    v_record = p_cursor.fetchone()

    if v_record is not None:
        v_blob_data = v_record[0]
        v_gramps_id = v_record[1]
        v_father_handle = v_record[2]
        v_mother_handle = v_record[3]

        if v_blob_data is not None:
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#2._Family:
            v_family_data = pickle.loads(v_blob_data)

            v_gramps_id = v_family_data[1]
            v_father_handle = v_family_data[2]
            v_mother_handle = v_family_data[3]
            v_child_ref_list = v_family_data[4]
            v_type = v_family_data[5]
            v_event_ref_list = v_family_data[6]
            v_media_list = v_family_data[7]

    return [v_gramps_id, v_father_handle, v_mother_handle, v_child_ref_list, v_type, v_event_ref_list, v_media_list]


def decode_person_data(p_person_handle, p_cursor):
    # v_given_name = ""
    # v_surname = ""
    # v_call_name = ""

    v_person_data = []

    # v_handle = ""
    # v_gramps_id = ""
    # v_gender = 2
    # v_primary_name = []
    # v_alternate_name = []
    # v_death_ref_index = -1
    # v_birth_ref_index = -1
    # v_event_ref_list = []
    # v_family_list = []
    # v_parent_family_list = []
    # v_media_base = []
    # v_address_base = []
    # v_attribute_base = []
    # v_url_base = []
    # v_lds_ord_base = []
    # v_citation_base = []
    # v_note_base = []
    # v_change = 0
    # v_tag_base = []
    # v_private = False
    # v_person_ref_list = []

    p_cursor.execute('SELECT given_name, surname, blob_data FROM person WHERE handle=?', [p_person_handle])
    v_record = p_cursor.fetchone()

    # Debug
    # logging.debug('v_record: '.join(map(str, v_record)))

    if v_record is not None:
        # v_given_name = v_record[0]
        # v_surname = v_record[1]
        v_blob_data = v_record[2]

        if v_blob_data is not None:
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#1._Person
            v_person_data = pickle.loads(v_blob_data)
            v_person_data = list(v_person_data)

            # Debug
            # logging.debug('v_person_data: '.join(map(str, v_person_data)))

            # v_handle = v_person_data[0]
            # v_gramps_id = v_person_data[1]
            # v_gender = v_person_data[2]
            v_primary_name = v_person_data[3]
            # v_alternate_name = v_person_data[4]
            # v_death_ref_index = v_person_data[5]
            # v_birth_ref_index = v_person_data[6]
            # v_event_ref_list = v_person_data[7]
            # v_family_list = v_person_data[8]
            # v_parent_family_list = v_person_data[9]
            # v_media_base = v_person_data[10]
            # v_address_base = v_person_data[11]
            # v_attribute_base = v_person_data[12]
            # v_url_base = v_person_data[13]
            # v_lds_ord_base = v_person_data[14]
            # v_citation_base = v_person_data[15]
            # v_note_Base = v_person_data[16]
            # v_change = v_person_data[17]
            # v_tag_base = v_person_data[18]
            # v_private = v_person_data[19]
            # v_person_ref_list = v_person_data[20]

            v_call_name = v_primary_name[12]
            v_given_name = v_primary_name[4]
            v_surname = v_primary_name[5][0][1] + ' ' + v_primary_name[5][0][0]

            v_person_data[3] = [v_surname.strip(), v_given_name.strip(), v_call_name.strip()]  # Overwrite primary names

    return v_person_data


def get_person_notes_handles(p_person_handle, p_cursor):
    p_cursor.execute('SELECT ref_handle FROM reference WHERE obj_handle=? AND ref_class="Note"', [p_person_handle])
    v_notes_handles = p_cursor.fetchall()

    return v_notes_handles


def decode_note_data(p_note_handle, p_cursor):
    # v_handle = ""
    # v_gramps_id = ""
    # v_text = []
    # v_format = ""
    # v_type = []
    # v_change = 0
    # v_tag_base = []
    # v_private = False

    v_note_data = []

    p_cursor.execute('SELECT blob_data FROM note WHERE handle=?', [p_note_handle])
    v_record = p_cursor.fetchone()

    if v_record is not None:
        v_blob_data = v_record[0]

        if v_blob_data is not None:
            # See
            # https://www.gramps-project.org/wiki/index.php/Using_database_API#9._Note
            v_note_data = pickle.loads(v_blob_data)

            # Debug
            # logging.debug('v_note_data: '.join(map(str, v_note_data)))

            # v_handle = v_note_data[0]
            # v_gramps_id = v_note_data[1]
            v_text = v_note_data[2][0]
            # v_format = v_note_data[3]
            v_type = v_note_data[4][0]
            # v_change = v_note_data[5]
            # v_tag_base = v_note_data[6]
            # v_private = v_note_data[7]

            # Debug
            # logging.debug('v_note_data = %s', v_note_data)
            # logging.debug('v_text = %s', v_text)
            # logging.debug('v_type = %s', v_type)

    return v_note_data


def get_media_data(p_media_handle, p_cursor):
    # v_handle: str = ""
    # v_gramps_id = ""
    # v_path = ""
    # v_mime = ""
    # v_description = ""
    # v_check_sum = ""
    # v_attribute_base = []
    # v_citation_base = []
    # v_note_base = []
    # v_change = 0
    # v_data_base = ()
    # v_tag_base = []
    # v_private = False

    v_media_data = []

    # v_base_path = ""

    # Get base media path
    p_cursor.execute('SELECT value FROM metadata WHERE setting=?', ['media-path'])
    v_blob_data = p_cursor.fetchone()

    if v_blob_data is not None:
        v_base_path = pickle.loads(v_blob_data[0])

        # Get path for p_media_handle
        p_cursor.execute('SELECT blob_data FROM media WHERE handle=?', [p_media_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_media_data = pickle.loads(v_record[0])
            v_media_data = list(v_media_data)

            # v_handle = v_media_data[0]
            # v_gramps_id = v_media_data[1]
            v_path = v_media_data[2]
            # v_mime = v_media_data[3]
            # v_description = v_media_data[4]
            # v_check_sum = v_media_data[5]
            # v_attribute_base = v_media_data[6]
            # v_citation_base = v_media_data[7]
            # v_note_base = v_media_data[8]
            # v_change = v_media_data[9]
            # v_data_base = v_media_data[10]
            # v_tag_base = v_media_data[11]
            # v_private = v_media_data[12]

            # Debug
            # if v_gramps_id == "O0008":
            #     print("v_media_data: ", v_media_data)

            # Check whether path is relative or absolute
            v_path_object = pathlib.Path(v_path)
            if not v_path_object.is_absolute():
                # Relative path, add base path
                v_path_object = pathlib.Path.joinpath(pathlib.Path(v_base_path), v_path_object)

            v_media_data[2] = str(v_path_object.as_posix())

    return v_media_data


def get_tag_dictionary(p_cursor):
    v_tag_dictionary = {}

    p_cursor.execute('SELECT handle, name FROM tag')
    v_tag_data = p_cursor.fetchall()

    for v_tag in v_tag_data:
        v_tag_dictionary[v_tag[0]] = v_tag[1]

    # Debug
    # logging.debug("v_tag_dictionary: ".join(map(str, v_tag_dictionary)))

    return v_tag_dictionary


def get_tag_list(p_tag_handle_list, p_tag_dictionary):
    v_tag_list = []

    for v_tag_handle in p_tag_handle_list:
        v_tag_list.append(p_tag_dictionary[v_tag_handle])

    # Debug
    # logging.debug("v_tag_list: ".join(map(str, v_tag_list)))

    return v_tag_list
