# Formatted using "python3-autopep8 --in-place --aggressive --aggressive *.py"

import logging
import os

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

# Constants
c_publishable = 'Publishable'
c_document = 'Document'
c_photo = 'Photo'
c_source = 'Source'


class Person:
    """A class to write a chapter about a person"""

    @property
    def person_handle(self):
        return self.__person_handle

    @property
    def document_path(self):
        """

        @rtype: Full path of the document
        """
        return self.__document_path

    @property
    def gramps_id(self):
        """

        @rtype: id of the gramps database object
        """
        return self.__gramps_id

    @property
    def gender(self):
        """

        @rtype: the gender of the person
        """
        return self.__gender

    @property
    def given_names(self):
        """

        @rtype: All given names of the person
        """
        return self.__given_names

    @property
    def surname(self):
        """

        @rtype: The surname of the person
        """
        return self.__surname

    @property
    def father_handle(self):
        """

        @rtype: The Gramps ID of the father of the person
        """
        return self.__father_handle

    @property
    def mother_handle(self):
        """

        @rtype: Then Gramps ID of the mother of the person
        """
        return self.__mother_handle

    @property
    def children_handles_list(self):
        """

        @rtype: A list with the Gramps IDs of the children of the person
        """
        return self.__children_handles_list

    @property
    def source_status(self):
        return self.__source_status

    def __init__(self, person_handle, db_cursor, document_path='../book/', language='nl'):
        self.__person_handle = person_handle
        self.__cursor = db_cursor
        self.__document_path = document_path
        self.__language = language

        # Get basic person data
        v_person_data = decode_person_data(self.__person_handle, self.__cursor)
        self.__gramps_id = v_person_data[1]
        self.__gender = v_person_data[2]
        self.__surname = v_person_data[3][0]
        self.__given_names = v_person_data[3][1]
        self.__call_name = v_person_data[3][2]
        self.__event_ref_list = v_person_data[7]
        self.__family_list = v_person_data[8]
        self.__parent_family_list = v_person_data[9]
        self.__media_list = v_person_data[10]

        self.__note_base = v_person_data[16]
        # self.__notes_handles_list = GetPersonNotesHandles(self.__person_handle, self.__cursor)

        self.__partner_handle_list = get_partner_handles(self.__person_handle, self.__cursor)
        self.__children_handles_list = get_children_handles_by_person(self.__person_handle, self.__cursor)

        self.__father_handle = get_father_handle_by_person(self.__person_handle, self.__cursor)
        self.__mother_handle = get_mother_handle_by_person(self.__person_handle, self.__cursor)
        self.__sibling_handles_list = hsf.sort_person_list_by_birth(get_sibling_handles_old(self.__person_handle, self.__cursor), self.__cursor)

        self.__create_person_event_dictionary()
        self.__create_family_event_dictionary()

        # TODO: This is a tag list NOT related to one person; this does not belong here
        self.__tag_dictionary = get_tag_dictionary(self.__cursor)

        self.__source_status = self.__get_source_status()

    def __create_person_event_dictionary(self):
        # Create an event dictionary.
        # The key refers to the type of event (e.g. Profession); the value contains a list of events belonging to this event type (e.g. multiple professions within key Profession)
        # Key:[event info, event info 2, event info 3]
        self.__PersonEventInfoDict = {}
        for v_event_ref in self.__event_ref_list:
            v_event_handle = v_event_ref[3]
            v_event_info = decode_event_data(v_event_handle, self.__cursor)
            
            # Filter on role
            v_role_type = v_event_ref[4][0]
            if(v_role_type == c_role_primary) or (v_role_type == c_role_family):
                # Create a dictionary from event data. Use event type as key, and rest of event as data

                # Check whether event type already exists as key
                if v_event_info[0] in self.__PersonEventInfoDict:
                    # if so, append event info to the dictionary entry
                    self.__PersonEventInfoDict[v_event_info[0]].append(v_event_info[1:])
                else:
                    # Otherwise create a new entry
                    self.__PersonEventInfoDict[v_event_info[0]] = [v_event_info[1:]]

                # Add event media to personal media list
                self.__media_list = self.__media_list + v_event_info[4]

    def __create_family_event_dictionary(self):
        # Create an event dictionary.
        # The key refers to the type of event (e.g. Profession); the value contains a list of events belonging to this event type (e.g. multiple professions within key Profession)
        # Key:[event info, event info 2, event info 3]
        self.__FamilyEventInfoDict = {}
        for v_family_handle in self.__family_list:
            v_family_data = decode_family_data(v_family_handle, self.__cursor)
            v_family_events = v_family_data[5]
            self.__media_list = self.__media_list + v_family_data[6]  # Add family media to personal media list

            for v_event_ref in v_family_events:
                v_event_handle = v_event_ref[3]
                v_event_info = decode_event_data(v_event_handle, self.__cursor)
                
                # Filter on role
                v_role_type = v_event_ref[4][0]
                if(v_role_type == c_role_primary) or (v_role_type == c_role_family):
                    # Create a dictionary from event data. Use event type as key, and rest of event as data

                    # Check whether event type already exists as key
                    if v_event_info[0] in self.__FamilyEventInfoDict:
                        # if so, append event info to the dictionary entry
                        self.__FamilyEventInfoDict[v_event_info[0]].append(v_event_info[1:])
                    else:
                        # Otherwise create a new entry
                        self.__FamilyEventInfoDict[v_event_info[0]] = [v_event_info[1:]]

                    # Add event media to personal media list
                    self.__media_list = self.__media_list + v_event_info[4]

    def __get_source_status(self):
        """ Checks whether scans are available for the events birth, marriage and death """

        v_source_status = {'b': '', 'm': '', 'd': ''}  # birth, marriage, death

        # Birth / baptism
        v_media_list = []
        if c_event_birth in self.__PersonEventInfoDict:  # Birth
            v_event_info = self.__PersonEventInfoDict[c_event_birth]
            v_media_list.extend(v_event_info[0][3])

        if c_event_baptism in self.__PersonEventInfoDict:  # Baptism
            v_event_info = self.__PersonEventInfoDict[c_event_baptism]
            v_media_list.extend(v_event_info[0][3])

        if len(v_media_list) > 0:
            v_source_status['b'] = 'b'

        # Marriage
        for v_family_handle in self.__family_list:
            v_family_info = decode_family_data(v_family_handle, self.__cursor)
            v_event_ref_list = v_family_info[5]

            for v_event in v_event_ref_list:
                v_event_handle = v_event[3]
                v_event_info = decode_event_data(v_event_handle, self.__cursor)
                v_type = v_event_info[0]
                v_media_list = v_event_info[4]

                # 1 = Marriage, 2 = Marriage Settlement, 3 = Marriage License, 4 = Marriage Contract
                if (v_type == c_event_marriage or v_type == c_event_marriage_settlement or v_type == c_event_marriage_license or v_type == c_event_marriage_contract) and (len(v_media_list) > 0):
                    v_source_status['m'] = 'm'

        # Death / Burial
        v_media_list = []
        if c_event_death in self.__PersonEventInfoDict:  # Death
            v_event_info = self.__PersonEventInfoDict[c_event_death]
            v_media_list.extend(v_event_info[0][3])

        if c_event_burial in self.__PersonEventInfoDict:  # Burial
            v_event_info = self.__PersonEventInfoDict[c_event_burial]
            v_media_list.extend(v_event_info[0][3])

        if len(v_media_list) > 0:
            v_source_status['d'] = 'd'

        return v_source_status

    def __picture_with_note(self, p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect=None, p_position='i'):
        # Latex Debug
        p_level.append(pl.NoEscape("% hkPersonChapter.Person.__picture_with_note"))

        self.__document_with_note(p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect, p_position)

    def __document_with_note(self, p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect=None, p_position='i'):
        # Add note(s)
        v_note_text = ''
        for v_note_handle in p_image_note_handles:
            v_note_data = decode_note_data(v_note_handle, self.__cursor)
            v_note_text = v_note_data[2][0]

            v_pos_1 = v_note_text.find("http")
            if v_pos_1 >= 0:  # 202303113
                # Check whether the note contains a web address
                # ...it does, first find '//'..
                v_pos_2 = v_note_text.find('//')

                # ...from that position find the next '/'
                v_pos_2 = v_note_text.find('/', v_pos_2+2)

                # ...find the end of the web address
                v_pos_3 = v_pos_2
                while (v_pos_3 < len(v_note_text)) and (v_note_text[v_pos_3] != ' '):
                    v_pos_3 = v_pos_3 + 1

                v_full_web_address = v_note_text[v_pos_1:v_pos_3]
                v_short_web_address = "<WebLink>"  # v_note_text[v_pos_1:v_pos_2]

                # Debug logging
                logging.debug("v_full_web_address: %s", v_full_web_address)
                logging.debug("v_short_web_address: %s", v_short_web_address)

                if v_pos_1 == 0:
                    # ...and create a link to the source...
                    v_note_text = r'Link to source: \href{' + v_full_web_address + '}{' + v_short_web_address + r'}' + r'\par '
                else:
                    # ...and create a link in the note...
                    v_note_text = v_note_text.replace(v_full_web_address, r'\href{' + v_full_web_address + '}{' + v_short_web_address + r'}' + r'\par ')
            else:
                v_note_text = v_note_text + r' \par '
#            vTagHandleList = v_note_data[6]

        # Check on portait vs landscape
        v_image = Image.open(p_image_path, mode='r')
        v_width, v_height = v_image.size
        if p_image_rect is not None:
            v_width = v_width * (p_image_rect[2] - p_image_rect[0]) / 100
            v_height = v_height * (p_image_rect[3] - p_image_rect[1]) / 100

        # Start a minipage
        p_level.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

        # Create the figure
        if v_width > v_height:
            # Landscape
            hsf.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.70\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)
        else:
            # Portrait
            hsf.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.50\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)

        # End the minipage
        p_level.append(pl.NoEscape(r'\end{minipage}'))
        p_level.append(pl.NoEscape(r'\vfill'))

    def __get_filtered_photo_list(self):
        v_photo_list = []

        for vMediaItem in self.__media_list:
            v_media_handle = vMediaItem[4]
            v_media_rect = vMediaItem[5]  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media_data = get_media_data(v_media_handle, self.__cursor)
            v_media_mime = v_media_data[3]
            v_tag_handle_list = v_media_data[11]

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in get_tag_list(v_tag_handle_list, self.__tag_dictionary)) and (c_photo in get_tag_list(v_tag_handle_list, self.__tag_dictionary)):
                    # v_photo_list.append(v_media_handle) # 20220328
                    v_photo_list.append([v_media_handle, v_media_rect])

        return v_photo_list

    def __get_filtered_document_list(self):
        v_document_list = []

        for vMediaItem in self.__media_list:
            v_media_handle = vMediaItem[4]
            v_media_rect = vMediaItem[5]  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media_data = get_media_data(v_media_handle, self.__cursor)
            v_media_mime = v_media_data[3]
            v_tag_handle_list = v_media_data[11]

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in get_tag_list(v_tag_handle_list, self.__tag_dictionary)) and (c_document in get_tag_list(v_tag_handle_list, self.__tag_dictionary)):
                    v_document_list.append([v_media_handle, v_media_rect])

        return v_document_list

    def __get_filtered_note_list(self, p_note_handle_list):
        """
        Removes all notes from p_note_handle_list that are of type 'Citation' or that are tagged 'Source'
        """

        v_note_list = []

        for v_note_handle in p_note_handle_list:
            v_note_data = decode_note_data(v_note_handle, self.__cursor)
            v_tag_handle_list = v_note_data[6]
            v_type = v_note_data[4][0]

            if not (c_source in get_tag_list(v_tag_handle_list, self.__tag_dictionary)) and not (v_type == c_note_citation):
                v_note_list.append(v_note_handle)

        return v_note_list

    def __write_life_sketch_section(self, p_level):
        # Create section with Life Sketch
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))

        with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('life sketch', self.__language), pLabel=False) as v_sub_level:
            # Create a story line
            v_life_sketch = ""

            # Check whether lifestories already exist in the notes
            for v_note in self.__note_base:
                v_note_handle = v_note
                v_note_data = decode_note_data(v_note_handle, self.__cursor)
                v_note_text = v_note_data[2][0]
                v_note_type = v_note_data[4][0]
                if v_note_type == c_note_person:  # Person Note
                    v_life_sketch = v_life_sketch + pu.escape_latex(v_note_text)

            # If no specific life stories were found, then write one
            if len(v_life_sketch) == 0:
                v_full_name = self.__given_names + ' ' + self.__surname
                v_he_she = hlg.translate('He', self.__language)
                v_his_her = hlg.translate('His', self.__language)
                v_brother_sister = hlg.translate('Brother', self.__language)
                v_father_mother = hlg.translate('Father', self.__language)
                if self.__gender == c_gender_female:
                    v_he_she = hlg.translate('She', self.__language)
                    v_his_her = hlg.translate('Her', self.__language)
                    v_brother_sister = hlg.translate('Sister', self.__language)
                    v_father_mother = hlg.translate('Mother', self.__language)

                v_vital_events = c_vital_events_set.intersection(self.__PersonEventInfoDict.keys())

                # Geboorte
                if c_event_birth in v_vital_events:  # Birth
                    v_string = hlg.translate("{0} was born on {1}", self.__language).format(pu.escape_latex(v_full_name), hsf.date_to_text(self.__PersonEventInfoDict[c_event_birth][0][0], False))
                    v_life_sketch = v_life_sketch + v_string

                    if (len(self.__PersonEventInfoDict[c_event_birth][0][1]) > 0) and (self.__PersonEventInfoDict[c_event_birth][0][1] != '-'):
                        v_string = hlg.translate("in {0}", self.__language).format(hsf.place_to_text(self.__PersonEventInfoDict[c_event_birth][0][1]))
                        v_life_sketch = v_life_sketch + ' ' + v_string

                    v_life_sketch = v_life_sketch + r". "

                elif c_event_baptism in v_vital_events:  # Baptism
                    v_string = hlg.translate("{0} was born about {1}", self.__language).format(pu.escape_latex(v_full_name), hsf.date_to_text(self.__PersonEventInfoDict[c_event_baptism][0][0], False))
                    v_life_sketch = v_life_sketch + v_string

                    if (len(self.__PersonEventInfoDict[c_event_baptism][0][1]) > 0) and (self.__PersonEventInfoDict[c_event_baptism][0][1] != '-'):
                        v_string = hlg.translate("in {0}", self.__language).format(hsf.place_to_text(self.__PersonEventInfoDict[c_event_baptism][0][1]))
                        v_life_sketch = v_life_sketch + ' ' + v_string

                    v_life_sketch = v_life_sketch + r". "

                # Roepnaam
                v_use_name = self.__given_names
                if len(self.__call_name) > 0:
                    v_use_name = self.__call_name
                    v_string = hlg.translate("{0} call name was {1}.", self.__language).format(v_his_her, pu.escape_latex(self.__call_name))
                    v_life_sketch = v_life_sketch + v_string

                if len(v_life_sketch) > 0:
                    v_life_sketch = v_life_sketch + r"\par "

                # Sisters and brothers
                v_number_sisters = 0
                v_number_brothers = 0
                v_sibling_names = []
                for v_sibling_handle in self.__sibling_handles_list:
                    v_sibling_data = decode_person_data(v_sibling_handle, self.__cursor)
                    if v_sibling_data[2] == 0:
                        v_number_sisters = v_number_sisters + 1
                    elif v_sibling_data[2] == 1:
                        v_number_brothers = v_number_brothers + 1

                    v_sibling_names.append(v_sibling_data[3][1])

                if v_number_sisters + v_number_brothers > 0:
                    v_string = ''
                    if v_number_sisters == 1 and v_number_brothers == 0:
                        v_string = hlg.translate("{0} had one sister:", self.__language).format(v_use_name)

                    if v_number_sisters > 1 and v_number_brothers == 0:
                        v_string = hlg.translate("{0} had {1} sisters:", self.__language).format(v_use_name, v_number_sisters)

                    if v_number_sisters == 0 and v_number_brothers == 1:
                        v_string = hlg.translate("{0} had one brother:", self.__language).format(v_use_name)

                    if v_number_sisters == 0 and v_number_brothers > 1:
                        v_string = hlg.translate("{0} had {1} brothers:", self.__language).format(v_use_name, v_number_brothers)

                    if v_number_sisters > 0 and v_number_brothers > 0:
                        v_string = hlg.translate("{0} was {1} of", self.__language).format(v_use_name, v_brother_sister.lower())

                    v_life_sketch = v_life_sketch + v_string + ' '

                    if len(v_sibling_names) > 1:
                        for vSiblingName in v_sibling_names[:-1]:
                            v_life_sketch = v_life_sketch + pu.escape_latex(vSiblingName) + ", "

                        v_life_sketch = v_life_sketch + hlg.translate("and", self.__language) + ' ' + pu.escape_latex(v_sibling_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "
                    elif len(v_sibling_names) == 1:
                        v_life_sketch = v_life_sketch + pu.escape_latex(v_sibling_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "

                # Partners and Children
                v_number_daughters = 0
                v_number_sons = 0
                v_child_names = []
                for v_child_handle in self.__children_handles_list:
                    v_child_data = decode_person_data(v_child_handle, self.__cursor)
                    if v_child_data[2] == 0:
                        v_number_daughters = v_number_daughters + 1
                    elif v_child_data[2] == 1:
                        v_number_sons = v_number_sons + 1

                    v_child_names.append(v_child_data[3][1])

                if v_number_daughters + v_number_sons > 0:
                    v_string = ''
                    if v_number_daughters == 1 and v_number_sons == 0:
                        v_string = hlg.translate("{0} had one daughter:", self.__language).format(v_full_name)
                        if len(v_life_sketch) > 0:
                            v_string = hlg.translate("Furthermore, {0} had one daughter:", self.__language).format(v_use_name)

                    if v_number_daughters > 1 and v_number_sons == 0:
                        v_string = hlg.translate("{0} had {1} daughters:", self.__language).format(v_full_name, v_number_daughters)
                        if len(v_life_sketch) > 0:
                            v_string = hlg.translate("Furthermore, {0} had {1} daughters:", self.__language).format(v_use_name, v_number_daughters)

                    if v_number_daughters == 0 and v_number_sons == 1:
                        v_string = hlg.translate("{0} had one son:", self.__language).format(v_full_name)
                        if len(v_life_sketch) > 0:
                            v_string = hlg.translate("Furthermore, {0} had one son:", self.__language).format(v_use_name)

                    if v_number_daughters == 0 and v_number_sons > 1:
                        v_string = hlg.translate("{0} had {1} sons:", self.__language).format(v_full_name, v_number_sons)
                        if len(v_life_sketch) > 0:
                            v_string = hlg.translate("Furthermore, {0} had {1} sons:", self.__language).format(v_use_name, v_number_sons)

                    if v_number_daughters > 0 and v_number_sons > 0:
                        v_string = hlg.translate("{0} was {1} of", self.__language).format(v_full_name, v_father_mother.lower())
                        if len(v_life_sketch) > 0:
                            v_string = hlg.translate("Furthermore, {0} was {1} of", self.__language).format(v_use_name, v_father_mother.lower())

                    v_life_sketch = v_life_sketch + v_string + ' '

                    if len(v_child_names) > 1:
                        for v_child_name in v_child_names[:-1]:
                            v_life_sketch = v_life_sketch + pu.escape_latex(v_child_name) + ", "

                        v_life_sketch = v_life_sketch + hlg.translate("and", self.__language) + ' ' + pu.escape_latex(v_child_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "
                    elif len(v_child_names) == 1:
                        v_life_sketch = v_life_sketch + pu.escape_latex(v_child_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "

                # Overlijden
                if c_event_death in v_vital_events:  # Death
                    v_string = hlg.translate("{0} died on {1}", self.__language).format(v_he_she, hsf.date_to_text(self.__PersonEventInfoDict[c_event_death][0][0], False))
                    v_life_sketch = v_life_sketch + v_string

                    if (len(self.__PersonEventInfoDict[c_event_death][0][1]) > 0) and (self.__PersonEventInfoDict[c_event_death][0][1] != '-'):
                        v_string = hlg.translate("in {0}.", self.__language).format(hsf.place_to_text(self.__PersonEventInfoDict[c_event_death][0][1]))
                        v_life_sketch = v_life_sketch + ' ' + v_string
                    else:
                        v_life_sketch = v_life_sketch + ". "

                elif c_event_burial in v_vital_events:  # Burial
                    v_string = hlg.translate("{0} died about {1}", self.__language).format(v_he_she, hsf.date_to_text(self.__PersonEventInfoDict[c_event_burial][0][0], False))
                    v_life_sketch = v_life_sketch + v_string

                    if (len(self.__PersonEventInfoDict[c_event_burial][0][1]) > 0) and (self.__PersonEventInfoDict[c_event_burial][0][1] != '-'):
                        v_string = hlg.translate("and was buried in {0}.", self.__language).format(hsf.place_to_text(self.__PersonEventInfoDict[c_event_burial][0][1]))
                        v_life_sketch = v_life_sketch + ' ' + v_string + ' '
                    else:
                        v_life_sketch = v_life_sketch + ". "

            v_life_sketch = v_life_sketch.replace(r"\n\n", r"\par")  # Replace double newline characters with \par
            v_life_sketch = v_life_sketch.replace(r"\newline%\newline", r"par")  # Replace double newline characters with \par

            v_portrait_found = False
            for v_media_item in self.__media_list:
                v_media_handle = v_media_item[4]
                v_media_data = get_media_data(v_media_handle, self.__cursor)
                v_media_path = v_media_data[2]
                # v_media_mime = v_media_data[3]
                # v_media_description = v_media_data[4]
                v_tag_handle_list = v_media_data[11]

                if 'Portrait' in get_tag_list(v_tag_handle_list, self.__tag_dictionary):
                    v_portrait_found = True
                    hsf.wrap_figure(v_sub_level, p_filename=v_media_path, p_width=r'0.35\textwidth', p_text=v_life_sketch)

            if not v_portrait_found:
                v_sub_level.append(pl.NoEscape(v_life_sketch))

        v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_vital_information_section(self, p_level):
        # Create section with Vital Information
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('vital information', self.__language), pLabel=False) as v_sub_level:
            with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                if len(self.__call_name) > 0:
                    v_table.add_row([hlg.translate('call name', self.__language) + ":", self.__call_name])

                if self.__gender in c_gender_dict:
                    v_table.add_row([hlg.translate('gender', self.__language) + ":", hlg.translate(c_gender_dict[self.__gender], self.__language)])

                for v_event in self.__PersonEventInfoDict.keys():
                    if v_event in c_vital_events_set:
                        v_string_1 = "Date of " + c_event_type_dict[v_event]
                        v_string_2 = "Place of " + c_event_type_dict[v_event]

                        v_string3 = hsf.date_to_text(self.__PersonEventInfoDict[v_event][0][0], False)
                        v_string4 = hsf.place_to_text(self.__PersonEventInfoDict[v_event][0][1], True)

                        if len(v_string3) > 0:
                            v_table.add_row([hlg.translate(v_string_1, self.__language) + ":", v_string3])
                        if len(v_string4) > 0:
                            v_table.add_row([hlg.translate(v_string_2, self.__language) + ":", v_string4])

            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_parental_section_graph(self, p_level):
        # Add Family graph
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('parental family', self.__language), pLabel=False) as v_sub_level:
            # Create a sorted list of self and siblings
            v_sibling_list = [self.__person_handle]
            for v_sibling_handle in self.__sibling_handles_list:
                v_sibling_list.append(v_sibling_handle)

            v_sibling_list = hsf.sort_person_list_by_birth(v_sibling_list, self.__cursor)

            # Create nodes
            v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
            v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

            # Parents
            v_father_name = hlg.translate('Unknown', self.__language)
            if self.__father_handle is not None:
                v_father_data = decode_person_data(self.__father_handle, self.__cursor)
                v_father_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_father_data[3][1], v_father_data[3][0], v_father_data[1]))

            v_mother_name = hlg.translate('Unknown', self.__language)
            if self.__mother_handle is not None:
                v_mother_data = decode_person_data(self.__mother_handle, self.__cursor)
                v_mother_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_mother_data[3][1], v_mother_data[3][0], v_mother_data[1]))

            # First row
            v_sub_level.append(pu.NoEscape(r'\node (father) [left, man]    {\small ' + v_father_name + r'}; &'))
            v_sub_level.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
            v_sub_level.append(pu.NoEscape(r'\node (mother) [right, woman] {\small ' + v_mother_name + r'};\\'))

            # Empty row
            v_string: str = r' & & \\'
            v_sub_level.append(pu.NoEscape(v_string))

            # Next one row per sibling
            v_counter = 0
            for v_sibling_handle in v_sibling_list:
                v_counter = v_counter + 1
                v_sibling_data = decode_person_data(v_sibling_handle, self.__cursor)
                v_sibling_id = v_sibling_data[1]
                v_sibling_gender = v_sibling_data[2]

                if v_sibling_id == self.__gramps_id:
                    v_sibling_name = self.__given_names + ' ' + self.__surname
                else:
                    v_sibling_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_sibling_data[3][1], v_sibling_data[3][0], v_sibling_data[1]))

                if v_sibling_gender == 0:  # Female
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, woman'
                elif v_sibling_gender == 1:  # Male
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man'
                else:
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man'

                if v_sibling_id == self.__gramps_id:
                    v_string = v_string + r', self'

                v_string = v_string + r'] {\small ' + v_sibling_name + r'}; \\'
                v_sub_level.append(pu.NoEscape(v_string))

            v_sub_level.append(pu.NoEscape(r'};'))

            # Create the graph
            v_sub_level.append(pu.NoEscape(r'\graph [use existing nodes] {'))
            v_sub_level.append(pu.NoEscape(r'father -- p0 -- mother;'))

            for v_count in range(1, v_counter + 1):
                v_sub_level.append(pu.NoEscape(r'p0 -> [vh path] p' + str(v_count) + r';'))

            v_sub_level.append(pu.NoEscape(r'};'))
            v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_parental_subsection_table(self, p_level):
        # Add Family table
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('parental family', self.__language), pLabel=False) as vSubLevel:
            with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                v_father_name = hlg.translate('Unknown', self.__language)
                if self.__father_handle is not None:
                    v_father_data = decode_person_data(self.__father_handle, self.__cursor)
                    v_father_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_father_data[3][1], v_father_data[3][0], v_father_data[1]))

                v_table.add_row([hlg.translate('father', self.__language) + ":", v_father_name])

                v_mother_name = hlg.translate('Unknown', self.__language)
                if self.__mother_handle is not None:
                    v_mother_data = decode_person_data(self.__mother_handle, self.__cursor)
                    v_mother_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_mother_data[3][1], v_mother_data[3][0], v_mother_data[1]))

                v_table.add_row([hlg.translate('mother', self.__language) + ":", v_mother_name])

                for v_sibling_handle in self.__sibling_handles_list:
                    v_sibling_data = decode_person_data(v_sibling_handle, self.__cursor)
                    if v_sibling_data[1] == self.__gramps_id:
                        v_sibling_type = hlg.translate('self', self.__language) + ":"
                    elif v_sibling_data[2] == 0:
                        v_sibling_type = hlg.translate('sister', self.__language) + ":"
                    elif v_sibling_data[2] == 1:
                        v_sibling_type = hlg.translate('brother', self.__language) + ":"
                    else:
                        v_sibling_type = hlg.translate('unknown', self.__language) + ":"

                    v_table.add_row([v_sibling_type, pl.NoEscape(hlt.GetPersonNameWithReference(v_sibling_data[3][1], v_sibling_data[3][0], v_sibling_data[1]))])

            vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_partner_sections_graph(self, p_level):
        # Add families with partners
        for v_partner_handle in self.__partner_handle_list:
            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner_data = decode_person_data(v_partner_handle, self.__cursor)
                v_partner_gramps_id = v_partner_data[1]
                v_partner_surname = v_partner_data[3][0]
                v_partner_given_names = v_partner_data[3][1]

                # For each partner create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hlt.CreateSubLevel(pLevel=p_level, pTitle=pl.NoEscape(hlt.GetPersonNameWithReference(v_partner_given_names, v_partner_surname, v_partner_gramps_id)), pLabel=False) as vSubLevel:
                    if self.__gender == 0:
                        v_family_handle = get_family_handle_by_father_mother(v_partner_handle, self.__person_handle, self.__cursor)
                    else:
                        v_family_handle = get_family_handle_by_father_mother(self.__person_handle, v_partner_handle, self.__cursor)

                    if v_family_handle is not None:
                        v_family_handle = v_family_handle[0]

                        # Nieuw
                        v_family_info = decode_family_data(v_family_handle, self.__cursor)
                        # v_family_gramps_id = v_family_info[0]
                        v_family_event_ref_list = v_family_info[5]

                        v_family_event_info_dict = {}
                        for v_family_event_ref in v_family_event_ref_list:
                            v_family_event_handle = v_family_event_ref[3]
                            v_family_event_info = decode_event_data(v_family_event_handle, self.__cursor)
                            if v_family_event_info[0] in v_family_event_info_dict:
                                v_family_event_info_dict[v_family_event_info[0]].append(v_family_event_info[1:])
                            else:
                                v_family_event_info_dict[v_family_event_info[0]] = [v_family_event_info[1:]]

                        # OUD
                        v_family_events = c_family_events_set.intersection(v_family_event_info_dict.keys())
                        if v_family_events:
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.translate('family events', self.__language), pLabel=False) as v_sub_sub_level:
                                with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                    for vEvent in v_family_events:
                                        v_string_1 = "Date of " + c_event_type_dict[vEvent]
                                        v_string_2 = "Place of " + c_event_type_dict[vEvent]
                                        v_string_3 = hsf.date_to_text(v_family_event_info_dict[vEvent][0][0], False)
                                        v_string_4 = hsf.place_to_text(v_family_event_info_dict[vEvent][0][1], True)

                                        if len(v_string_3) > 0:
                                            v_table.add_row([hlg.translate(v_string_1, self.__language) + ":", v_string_3])
                                        if len(v_string_4) > 0:
                                            v_table.add_row([hlg.translate(v_string_2, self.__language) + ":", v_string_4])

                                v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                            # Add subchapter for children
                            v_children_handles = get_children_handles_by_family(v_family_handle, self.__cursor)
                            if len(v_children_handles) > 0:
                                # If children exist, then create subchapter and a table
                                with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.translate('children', self.__language), pLabel=False) as v_sub_sub_level:
                                    v_father_string = ''
                                    v_mother_string = ''

                                    v_sub_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                                    v_sub_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                                    # Self
                                    v_name = pl.NoEscape(self.given_names + ' ' + self.__surname)
                                    if self.__gender == 0:  # Female
                                        v_mother_string = r'\node (mother) [right, woman, self] {\small ' + v_name + r'};'
                                    else:  # Male
                                        v_father_string = r'\node (father) [left, man, self] {\small ' + v_name + r'};'

                                    # Partner
                                    v_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_partner_data[3][1], v_partner_data[3][0], v_partner_data[1]))
                                    if v_partner_data[2] == 0:  # Female
                                        v_mother_string = r'\node (mother) [right, woman] {\small ' + v_name + r'};'
                                    else:  # Male
                                        v_father_string = r'\node (father) [left, man] {\small ' + v_name + r'};'

                                    # First row
                                    v_sub_sub_level.append(pu.NoEscape(v_father_string + r' &'))
                                    v_sub_sub_level.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
                                    v_sub_sub_level.append(pu.NoEscape(v_mother_string + r' \\'))

                                    # Empty row
                                    v_string = r' & & \\'
                                    v_sub_sub_level.append(pu.NoEscape(v_string))

                                    # Next one row per child
                                    v_counter = 0

                                    # Children
                                    for vChildHandle in v_children_handles:
                                        v_counter = v_counter + 1
                                        v_child_data = decode_person_data(vChildHandle, self.__cursor)
                                        v_child_name = pl.NoEscape(hlt.GetPersonNameWithReference(v_child_data[3][1], v_child_data[3][0], v_child_data[1]))

                                        if v_child_data[2] == 0:  # Female
                                            v_string = r' & & \node (p' + str(v_counter) + r') [right, woman] {\small ' + v_child_name + r'}; \\'
                                        elif v_child_data[2] == 1:  # Male
                                            v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + v_child_name + r'}; \\'
                                        else:
                                            v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + v_child_name + r'}; \\'

                                        v_sub_sub_level.append(pu.NoEscape(v_string))

                                    v_sub_sub_level.append(pu.NoEscape(r'};'))

                                    # Create the graph
                                    v_sub_sub_level.append(pu.NoEscape(r'\graph [use existing nodes] {'))
                                    v_sub_sub_level.append(pu.NoEscape(r'father -- p0 -- mother;'))

                                    for v_count in range(1, v_counter + 1):
                                        v_sub_sub_level.append(pu.NoEscape(r'p0 -> [vh path] p' + str(v_count) + r';'))

                                    v_sub_sub_level.append(pu.NoEscape(r'};'))
                                    v_sub_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
                                    v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_partner_sections_table(self, p_level):
        # Add families with partners
        for v_partner_handle in self.__partner_handle_list:
            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner_data = decode_person_data(v_partner_handle, self.__cursor)
                v_partner_gramps_id = v_partner_data[1]
                v_partner_surname = v_partner_data[3][0]
                v_partner_given_names = v_partner_data[3][1]

                # For each partner create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hlt.CreateSubLevel(pLevel=p_level, pTitle=pl.NoEscape(hlt.GetPersonNameWithReference(v_partner_given_names, v_partner_surname, v_partner_gramps_id)), pLabel=False) as vSubLevel:
                    if self.__gender == 0:
                        v_family_handle = get_family_handle_by_father_mother(v_partner_handle, self.__person_handle, self.__cursor)
                    else:
                        v_family_handle = get_family_handle_by_father_mother(self.__person_handle, v_partner_handle, self.__cursor)

                    if v_family_handle is not None:
                        v_family_handle = v_family_handle[0]

                        # Nieuw
                        v_family_info = decode_family_data(v_family_handle, self.__cursor)
                        # v_family_gramps_id = v_family_info[0]
                        v_family_event_ref_list = v_family_info[5]

                        v_family_event_info_dict = {}
                        for v_family_event_ref in v_family_event_ref_list:
                            v_family_event_handle = v_family_event_ref[3]
                            v_family_event_info = decode_event_data(v_family_event_handle, self.__cursor)
                            if v_family_event_info[0] in v_family_event_info_dict:
                                v_family_event_info_dict[v_family_event_info[0]].append(v_family_event_info[1:])
                            else:
                                v_family_event_info_dict[v_family_event_info[0]] = [v_family_event_info[1:]]

                        # OUD
                        v_family_events = c_family_events_set.intersection(v_family_event_info_dict.keys())
                        if v_family_events:
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.translate('family events', self.__language), pLabel=False) as v_sub_sub_level:
                                with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                    for vEvent in v_family_events:
                                        v_string_1 = "Date of " + c_event_type_dict[vEvent]
                                        v_string_2 = "Place of " + c_event_type_dict[vEvent]
                                        v_table.add_row([hlg.translate(v_string_1, self.__language) + ":", hsf.date_to_text(v_family_event_info_dict[vEvent][0][0], False)])
                                        v_table.add_row([hlg.translate(v_string_2, self.__language) + ":", hsf.place_to_text(v_family_event_info_dict[vEvent][0][1], True)])

                                v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                        # Add subchapter for children
                        v_children_handles = get_children_handles_by_family(v_family_handle, self.__cursor)
                        if len(v_children_handles) > 0:
                            # If children exist, then create subchapter and a table
                            with hlt.CreateSubLevel(pLevel=vSubLevel, pTitle=hlg.translate('children', self.__language), pLabel=False) as v_sub_sub_level:
                                with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                    for v_child_handle in v_children_handles:
                                        # For each child create a separate row
                                        # in the table
                                        v_child_data = decode_person_data(v_child_handle, self.__cursor)
                                        if v_child_data[2] == 0:
                                            v_child_type = hlg.translate('daughter', self.__language) + ":"
                                        elif v_child_data[2] == 1:
                                            v_child_type = hlg.translate('son', self.__language) + ":"
                                        else:
                                            v_child_type = hlg.translate('unknown', self.__language) + ":"

                                        v_table.add_row([v_child_type, pl.NoEscape(hlt.GetPersonNameWithReference(v_child_data[3][1], v_child_data[3][0], v_child_data[1]))])

                                v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_family_section(self, p_level):
        """
        Create a section listing all family relationships
        """

        # Create section with Family Information
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with p_level.create(hlt.Section(title=hlg.translate('family', self.__language), label=False)) as vSubLevel:
            self.__write_parental_section_graph(vSubLevel)
            self.__write_partner_sections_graph(vSubLevel)

    def __write_education_section(self, p_level):
        """
        Create a section with a table containing education
        """

        # Create section with Education ***
        v_education_events = c_education_events_set.intersection(self.__PersonEventInfoDict.keys())
        if v_education_events:
            v_education_list = []
            for v_event in v_education_events:
                v_education_list = v_education_list + self.__PersonEventInfoDict[v_event]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            v_education_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('education', self.__language), pLabel=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hlg.translate('date', self.__language)), pu.bold(hlg.translate('course', self.__language))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_education in v_education_list:
                        if len(v_education[2]) == 0:
                            v_education[2] = '-'

                        v_date = hsf.date_to_text(v_education[0])
                        v_course = v_education[2]
                        v_place = hsf.place_to_text(v_education[1], True)
                        v_table.add_row([v_date, pl.NoEscape(v_course) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_place)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_profession_section(self, p_level):
        """
        Create a section with a table containing working experiences
        """

        # Create section with Working Experience ***
        v_professional_events = c_professional_events_set.intersection(self.__PersonEventInfoDict.keys())
        if v_professional_events:
            v_professional_list = []
            for v_event in v_professional_events:
                v_professional_list = v_professional_list + self.__PersonEventInfoDict[v_event]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            v_professional_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('occupation', self.__language), pLabel=False) as vSubLevel:
                with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hlg.translate('date', self.__language)), pu.bold(hlg.translate('profession', self.__language))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_profession in v_professional_list:
                        if len(v_profession[2]) == 0:
                            v_profession[2] = '-'

                        v_date = hsf.date_to_text(v_profession[0])
                        v_job = v_profession[2]
                        v_place = hsf.place_to_text(v_profession[1], True)
                        v_table.add_row([v_date, pu.escape_latex(v_job) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_place)])

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_map(self, p_level):
        """
        Create a section with maps of all residences
        """

        #
        # Work in Progress
        #

        # Create section with Residential Information
        v_residential_events = c_residential_events_set.intersection(self.__PersonEventInfoDict.keys())
        if v_residential_events:
            # Create path name for map
            # v_path = self.__document_path + r'Figures'

            # Compose some temporary place type labeles
            v_city_label = c_place_type_dict[c_place_type_city]
            v_town_label = c_place_type_dict[c_place_type_town]
            v_village_label = c_place_type_dict[c_place_type_village]
            v_municipality_label = c_place_type_dict[c_place_type_municipality]
            v_country_label = c_place_type_dict[c_place_type_country]

            # Compose residence list
            v_residence_list = []
            for v_event in v_residential_events:
                v_residence_list = v_residence_list + self.__PersonEventInfoDict[v_event]

            # Create minipage
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('residences', self.__language), pLabel=False) as v_sub_level:
                # Create Tikz drawing with map as background
                # v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))

                # Create nodes
                v_scope_open = False
                v_done_list = []
                v_counter = 0
                for v_residence in v_residence_list:
                    v_counter = v_counter + 1

                    # Split date from place
                    # v_date = v_residence[0]
                    v_place = v_residence[1]

                    # Find place name and coordinates
                    v_name: str = '-'
                    v_latitude: float = 0.
                    v_longitude: float = 0.
                    # v_code: str = ''
                    if v_city_label in v_place:
                        v_name = v_place[v_city_label][0]
                        v_latitude = float(v_place[v_city_label][1][0])
                        v_longitude = float(v_place[v_city_label][1][1])
                        # v_code = v_place[v_city_label][2]
                    elif v_town_label in v_place:
                        v_name = v_place[v_town_label][0]
                        v_latitude = float(v_place[v_town_label][1][0])
                        v_longitude = float(v_place[v_town_label][1][1])
                        # v_code = v_place[v_town_label][2]
                    elif v_village_label in v_place:
                        v_name = v_place[v_village_label][0]
                        v_latitude = float(v_place[v_village_label][1][0])
                        v_longitude = float(v_place[v_village_label][1][1])
                        # v_code = v_place[v_village_label][2]
                    elif v_municipality_label in v_place:
                        v_name = v_place[v_municipality_label][0]
                        v_latitude = float(v_place[v_municipality_label][1][0])
                        v_longitude = float(v_place[v_municipality_label][1][1])
                        # v_code = v_place[v_municipality_label][2]
                    else:
                        print('Warning in hkPersonChapter.__WriteResidenceSection_Map: No valid city/village found in v_place: ', v_place)

                    # Debug
                    logging.debug('v_name, v_longitude, v_latititude: %s, %5.3f. %5.3f', v_name, v_longitude, v_latitude)
                    
                    if v_country_label in v_place:
                        v_country = v_place[v_country_label][0]
                        v_country_code = v_place[v_country_label][2]

                        if len(v_country_code) == 0:
                            v_country_code = v_country

                    # 20220109: Limit number of maps to Netherlands, Western Europe and the World
                    if v_country_code != 'NLD':
                        v_region_list = hsf.get_country_continent_subregion(v_country_code)
                        if v_region_list[1] == 'Western Europe':
                            v_country_code = 'WEU'
                        elif v_region_list[0] == 'Europe':
                            v_country_code = 'EUR'
                        else:
                            v_country_code = 'WLD'
                    
                    # Create path / file name for map
                    v_path = self.__document_path + r'Figures'
                    v_file_path = hsf.create_map(v_path, v_country_code)

                    if v_country_code not in v_done_list:
                        v_done_list.append(v_country_code)

                        # Check if scope is still open
                        if v_scope_open:
                            v_sub_level.append(pu.NoEscape(r'\end{scope}'))
                            v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))  # 20220109
                            v_scope_open = False

                        # Create node for background map
                        v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))  # 20220109
                        v_string = r'\node [inner sep=0] (' + v_country_code + r') {\includegraphics[width=10cm]{' + v_file_path + r'}};'
                        v_sub_level.append(pu.NoEscape(v_string))

                        # Create new scope with lower left corner (0,0) and upper right corner (1,1)
                        v_string = r'\begin{scope}[x={(' + v_country_code + r'.south east)},y={(' + v_country_code + r'.north west)}]'
                        v_sub_level.append(pu.NoEscape(v_string))
                        v_scope_open = True

                    # width and height in degrees
                    v_coordinates = hsf.get_country_min_max_coordinates(v_country_code)
                    v_map_lon0 = v_coordinates[0]
                    v_map_lat0 = v_coordinates[1]
                    v_map_lon1 = v_coordinates[2]
                    v_map_lat1 = v_coordinates[3]

                    # Debug
                    logging.debug('v_map_lon0, v_map_lat0, v_map_lon1, v_map_lat1: %5.3f, %5.3f, %5.3f, %5.3f', v_map_lon0, v_map_lat0, v_map_lon1, v_map_lat1)

                    # width and height in pixels
                    v_map_width = 0
                    v_map_height = 0
                    with Image.open(v_file_path, mode='r') as vImage:
                        v_map_width, v_map_height = vImage.size

                    # Debug
                    logging.debug('v_map_width, v_map_height: %d, %d', v_map_width, v_map_height)

                    # Convert to image coordinates
                    v_x = (v_longitude - v_map_lon0)/(v_map_lon1 - v_map_lon0)
                    v_y = (v_latitude - v_map_lat0)/(v_map_lat1 - v_map_lat0)
                    if v_x < 0 or v_y < 0:
                        logging.warning('Place off map. v_x, v_y: %5.3f, %5.3f', v_x, v_y)

                    v_string = r'\node (p' + str(v_counter) + r') at (' + str(v_x) + r', ' + str(v_y) + r') [point] {};'
                    v_sub_level.append(pu.NoEscape(v_string))

                # Create graph
                # v_sub_level.append(pu.NoEscape(r'\graph [use existing nodes] {'))
                #
                # for vCount in range(2, v_counter + 1):
                #     v_sub_level.append(pu.NoEscape(r'p' + str(vCount-1) + ' -> p' + str(vCount) + r';'))
                #
                # v_sub_level.append(pu.NoEscape(r'};'))
                if v_scope_open:
                    v_sub_level.append(pu.NoEscape(r'\end{scope}'))
                    v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
                    v_scope_open = False

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_timeline(self, p_level):
        """
        Create a section with a list of all residences in a graphical timeline format
        """

        # Create section with Residential Information
        v_residential_events = c_residential_events_set.intersection(self.__PersonEventInfoDict.keys())
        if v_residential_events:
            v_residence_list = []
            for v_event in v_residential_events:
                v_residence_list = v_residence_list + self.__PersonEventInfoDict[v_event]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            v_residence_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('residences', self.__language), pLabel=False) as v_sub_level:
                # Create nodes
                v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                v_counter = 0
                for v_residence in v_residence_list:
                    v_counter = v_counter + 1

                    v_start_date = hsf.get_start_date(v_residence[0])
                    v_address = hsf.street_to_text(v_residence[1])

                    v_string = r'\node (p' + str(v_counter) + r') [date] {\small ' + v_start_date + r'}; & '
                    v_string = v_string + r'\node [text width=10cm] {\small ' + pu.escape_latex(v_address) + r'};\\'
                    v_sub_level.append(pu.NoEscape(v_string))

                v_sub_level.append(pu.NoEscape(r'};'))

                # Create graph
                v_sub_level.append(pu.NoEscape(r'\graph [use existing nodes] {'))

                for v_count in range(2, v_counter + 1):
                    v_sub_level.append(pu.NoEscape(r'p' + str(v_count-1) + ' -> p' + str(v_count) + r';'))

                v_sub_level.append(pu.NoEscape(r'};'))
                v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_table(self, p_level):
        """
        Create a section with a list of all residences in a table format
        """

        # Create section with Residential Information
        v_residential_events = c_residential_events_set.intersection(self.__PersonEventInfoDict.keys())
        if v_residential_events:
            v_residence_list = []
            for vEvent in v_residential_events:
                v_residence_list = v_residence_list + self.__PersonEventInfoDict[vEvent]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
            v_residence_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('residences', self.__language), pLabel=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hlg.translate('date', self.__language)), pu.bold(hlg.translate('residence', self.__language))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    for v_residence in v_residence_list:
                        v_date = hsf.date_to_text(v_residence[0])
                        v_address = hsf.street_to_text(v_residence[1])
                        v_table.add_row([v_date, pu.escape_latex(v_address)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_photo_section(self, p_level):
        """
        Create section with photos
        """

        v_filtered_photo_list = self.__get_filtered_photo_list()
        if len(v_filtered_photo_list) > 0:
            # Allocate variables
            v_media_path_1 = None
            v_media_title_1 = None
            v_media_rect_1 = None
            v_media_path_2 = None
            v_media_title_2 = None
            v_media_rect_2 = None

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('photos', self.__language), pLabel=False) as v_sub_level:
                #
                # 1. All photos with notes
                #
                v_position = 'o'
                v_temp_list = v_filtered_photo_list.copy()  # Use temporary list, so items can be removed while iterating
                for vItem in v_temp_list:
                    v_media_handle = vItem[0]
                    v_media_rect = vItem[1]

                    v_media_data = get_media_data(v_media_handle, self.__cursor)
                    v_media_path = v_media_data[2]
                    v_media_title = v_media_data[4]
                    v_media_note_handles = v_media_data[8]
                    if len(v_media_note_handles) > 0:
                        # Picture contains notes, then special treatment
                        v_position = 'o' if v_position == 'i' else 'i'  # Alternate position of image / text
                        self.__picture_with_note(v_sub_level, v_media_path, v_media_title, v_media_note_handles, v_media_rect, v_position)

                        # Done, remove from list
                        v_filtered_photo_list.remove(vItem)

                #
                # 2. Remaining photos, side by side
                #
                v_counter = 0

                v_temp_list = v_filtered_photo_list.copy()  # Use temporary list, so items can be removed while iterating
                for vItem in v_temp_list:
                    v_media_handle = vItem[0]
                    v_media_rect = vItem[1]

                    v_media_data = get_media_data(v_media_handle, self.__cursor)
                    v_counter = v_counter + 1
                    if v_counter % 2 == 1:
                        v_media_path_1 = v_media_data[2]
                        v_media_title_1 = v_media_data[4]
                        v_media_rect_1 = v_media_rect

                        # Remove media_1 from list
                        v_filtered_photo_list.remove(vItem)
                    else:
                        v_media_path_2 = v_media_data[2]
                        v_media_title_2 = v_media_data[4]
                        v_media_rect_2 = v_media_rect

                        hsf.picture_side_by_side_equal_height(v_sub_level, v_media_path_1, v_media_path_2, v_media_title_1, v_media_title_2)

                        # Remove media_2 from list
                        v_filtered_photo_list.remove(vItem)

                        # Reset variables
                        v_media_path_1 = None
                        v_media_title_1 = None

                        v_media_path_2 = None
                        v_media_title_2 = None

                #
                # 3. In case temp list had an odd length, one document might be remaining
                #
                if v_media_path_1 is not None:
                    # Latex Debug
                    v_sub_level.append(pl.NoEscape("% hkPersonChapter.Person.__WritePhotoSection"))

                    # 20230313: Start a minipage
                    p_level.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

                    if v_media_rect_1 is not None:
                        # Set focus area 20220328
                        v_left_1 = '{' + str(v_media_rect_1[0]/100) + r'\wd1}'
                        v_right_1 = '{' + str(1-v_media_rect_1[2]/100) + r'\wd1}'
                        v_top_1 = '{' + str(v_media_rect_1[1]/100) + r'\ht1}'
                        v_bottom_1 = '{' + str(1-v_media_rect[3]/100) + r'\ht1}'

                        v_trim = v_left_1 + ' ' + v_bottom_1 + ' ' + v_right_1 + ' ' + v_top_1
                        v_sub_level.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + v_media_path_1 + r'"}}'))
                        v_sub_level.append(pl.NoEscape(r'\includegraphics[trim=' + v_trim + ', clip]{"' + v_media_path_1 + r'"}'))
                        v_sub_level.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(v_media_title_1) + '}'))

                        # v_sub_level.append(pl.NoEscape(r'\includegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + v_media_path_1 + r'"}}'))
                        # v_sub_level.append(pl.NoEscape(r'\caption{' + pu.escape_latex(v_media_title_1) + '}'))
                    else:
                        # 20230313
                        v_sub_level.append(pl.NoEscape(r'\includegraphics[width=\textwidth]{"' + v_media_path_1 + r'"}'))
                        v_sub_level.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(v_media_title_1) + '}'))

                        # with v_sub_level.create(hlt.Figure(position='htpb')) as vPhoto:
                        #     vPhoto.add_image(pl.NoEscape(v_media_path_1))
                        #     vPhoto.add_caption(pu.escape_latex(v_media_title_1))

                    # 20230313: End the minipage
                    p_level.append(pl.NoEscape(r'\end{minipage}'))

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_document_section(self, p_level):
        """
        Create section with document scans
        """

        v_filtered_document_list = self.__get_filtered_document_list()
        if len(v_filtered_document_list) > 0:
            # Allocate variables
            v_media_path_1 = None
            v_media_title_1 = None
            v_media_rect_1 = None
            v_media_path_2 = None
            v_media_title_2 = None
            v_media_rect_2 = None

            # Debug
            logging.debug("v_filtered_document_list: ".join(map(str, v_filtered_document_list)))

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hlt.CreateSubLevel(pLevel=p_level, pTitle=hlg.translate('documents', self.__language), pLabel=False) as v_sub_level:
                #
                # 1. All documents with notes
                #
                v_position = 'o'
                v_temp_list = v_filtered_document_list.copy()  # Use temporary list, so items can be removed while iterating
                for v_item in v_temp_list:
                    v_media_handle = v_item[0]
                    v_media_rect = v_item[1]

                    v_media_data = get_media_data(v_media_handle, self.__cursor)
                    v_media_path = v_media_data[2]
                    v_media_title = v_media_data[4]
                    v_media_note_handles = self.__get_filtered_note_list(v_media_data[8])

                    # TODO: dit gaat mis als het om een note met tag 'source' gaat
                    if len(v_media_note_handles) > 0:
                        # Document contains notes, then treatment
                        v_position = 'o' if v_position == 'i' else 'i'  # Alternate position of image / text
                        self.__document_with_note(v_sub_level, v_media_path, v_media_title, v_media_note_handles, v_media_rect, v_position)  # 20220322: Added v_media_rect

                        # Done, remove from list
                        v_filtered_document_list.remove(v_item)

                #
                # 2. Remaining documents, side by side
                #
                v_counter = 0

                v_temp_list = v_filtered_document_list.copy()  # Use temporary list, so items can be removed while iterating
                for v_item in v_temp_list:
                    v_media_handle = v_item[0]
                    v_media_rect = v_item[1]

                    v_media_data = get_media_data(v_media_handle, self.__cursor)

                    v_counter = v_counter + 1
                    if v_counter % 2 == 1:
                        v_media_path_1 = v_media_data[2]
                        v_media_title_1 = v_media_data[4]
                        v_media_rect_1 = v_media_rect

                        # Remove media_1 from list
                        v_filtered_document_list.remove(v_item)
                    else:
                        v_media_path_2 = v_media_data[2]
                        v_media_title_2 = v_media_data[4]
                        v_media_rect_2 = v_media_rect

                        hsf.picture_side_by_side_equal_height(v_sub_level, v_media_path_1, v_media_path_2, v_media_title_1, v_media_title_2, v_media_rect_1, v_media_rect_2)

                        # Remove media_2 from list
                        v_filtered_document_list.remove(v_item)

                        # Reset variables
                        v_media_path_1 = None
                        v_media_title_1 = None
                        v_media_rect_1 = None

                        v_media_path_2 = None
                        v_media_title_2 = None
                        v_media_rect_2 = None

                #
                # 3. In case temp list had an odd length, one document might be remaining
                #
                if v_media_path_1 is not None:
                    # Latex Debug
                    v_sub_level.append(pl.NoEscape("% hkPersonChapter.Person.__WriteDocumentSection"))

                    # 20230313: Start a minipage
                    p_level.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

                    if v_media_rect_1 is not None:
                        # 20220328: Set focus area
                        v_left_1 = '{' + str(v_media_rect_1[0]/100) + r'\wd1}'
                        v_right_1 = '{' + str(1-v_media_rect_1[2]/100) + r'\wd1}'
                        v_top_1 = '{' + str(v_media_rect_1[1]/100) + r'\ht1}'
                        v_bottom_1 = '{' + str(1-v_media_rect[3]/100) + r'\ht1}'

                        v_trim = v_left_1 + ' ' + v_bottom_1 + ' ' + v_right_1 + ' ' + v_top_1
                        v_sub_level.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + v_media_path_1 + r'"}}'))
                        v_sub_level.append(pl.NoEscape(r'\includegraphics[width=\textwidth, trim=' + v_trim + ', clip]{"' + v_media_path_1 + r'"}'))
                        v_sub_level.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(v_media_title_1) + '}'))

                        # v_sub_level.append(pl.NoEscape(r'\includegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + v_media_path_1 + r'"}}'))
                        # v_sub_level.append(pl.NoEscape(r'\caption{' + pu.escape_latex(v_media_title_1) + '}'))
                    else:
                        # 20230313
                        v_sub_level.append(pl.NoEscape(r'\includegraphics[width=\textwidth]{"' + v_media_path_1 + r'"}'))
                        v_sub_level.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(v_media_title_1) + '}'))

#                        with v_sub_level.create(hlt.Figure(position='htpb')) as vPhoto:
#                            vPhoto.add_image(pl.NoEscape(v_media_path_1))
#                            vPhoto.add_caption(pu.escape_latex(v_media_title_1))

                    # 20230313: End the minipage
                    p_level.append(pl.NoEscape(r'\end{minipage}'))

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def write_person_chapter(self):
        """
        Writes the person to a separate chapter in a subdocument
        """

        # Display progress
        print("Writing a chapter about: ", self.given_names, self.surname)

        # Create a new chapter for the active person
        v_chapter = hlt.Chapter(title=self.given_names + ' ' + self.surname, label=self.gramps_id)

        self.__write_life_sketch_section(v_chapter)
        self.__write_vital_information_section(v_chapter)
        # self.__WriteFamilySection(v_chapter)
        self.__write_parental_section_graph(v_chapter)
        self.__write_partner_sections_graph(v_chapter)

        self.__write_education_section(v_chapter)
        self.__write_profession_section(v_chapter)
        self.__write_residence_section_timeline(v_chapter)
        # self.__WriteResidenceSection_Map(v_chapter)
        self.__write_photo_section(v_chapter)
        self.__write_document_section(v_chapter)

        v_chapter.generate_tex(filepath=self.document_path + self.gramps_id)
