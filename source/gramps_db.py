import logging

import tag

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
    c_event_military_service,
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
    c_note_person: "PersonChapter",
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


def get_person_handle_by_gramps_id(p_person_id, p_cursor):
    p_cursor.execute('SELECT handle FROM person WHERE gramps_id=?', [p_person_id])
    v_person_handle = p_cursor.fetchone()

    if v_person_handle is not None:
        v_person_handle = v_person_handle[0]

    return v_person_handle


def get_tag_dictionary(p_cursor):
    v_tag_dictionary = {}

    p_cursor.execute('SELECT handle, name FROM tag')
    v_tag_data = p_cursor.fetchall()

    for v_tag in v_tag_data:
        v_tag_dictionary[v_tag[0]] = v_tag[1]

    # Debug
    # logging.debug("v_tag_dictionary: ".join(map(str, v_tag_dictionary)))

    return v_tag_dictionary


def get_tag_list(p_tag_list: list[tag.Tag], p_tag_dictionary: dict):
    v_tag_list: list[tag.Tag] = []

    for v_tag in p_tag_list:
        v_tag_list.append(p_tag_dictionary[v_tag.__handle__])

    # Debug
    logging.debug("v_tag_list: ".join(map(str, v_tag_list)))

    return v_tag_list
