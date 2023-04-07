import datetime
import logging

import hkDate
import hkEvent
import hkEventRef
import hkFamily
import hkGrampsDb
import hkLanguage
import hkLatex
import hkMedia
import hkNote
import hkPerson
import hkPersonRef
import hkPlace
import hkSupportFunctions

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu

from PIL import Image

# Prevents PIL.Image.DecompressionBombError: Image size (... pixels)
# exceeds limit of .... pixels, could be decompression bomb DOS attack.
Image.MAX_IMAGE_PIXELS = None

# Constants
c_publishable = 'Publishable'
c_document = 'Document'
c_photo = 'Photo'
c_source = 'Source'


class PersonChapter:
    """A class to write a chapter about a person"""

    def __init__(self, p_person_handle, p_cursor, document_path='../book/', language='nl'):
        self.__cursor__ = p_cursor
        self.__document_path__ = document_path
        self.__language__ = language

        # Get basic person data
        self.__person__ = hkPerson.Person(p_person_handle, p_cursor)

    def __picture_with_note(self, p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect=None, p_position='i'):
        # Latex Debug
        p_level.append(pl.NoEscape("% hkPersonChapter.PersonChapter.__picture_with_note"))

        self.__document_with_note(p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect, p_position)

    def __document_with_note(self, p_level, p_image_path, p_image_title, p_image_note_handles, p_image_rect=None, p_position='i'):
        # Add note(s)
        v_note_text = ''
        for v_note_handle in p_image_note_handles:
            v_note = hkNote.Note(v_note_handle, self.__cursor__)
            v_note_text = v_note.__note_text__

            v_pos_1 = v_note_text.find("http")
            # Check whether the note contains a web address
            if v_pos_1 >= 0:  # 202303113
                # ...it does, first find '//'..
                v_pos_2 = v_note_text.find('//')+2

                # ...find the end of the web address
                v_pos_4 = v_pos_2
                while (v_pos_4 < len(v_note_text)) and (v_note_text[v_pos_4] != ' '):
                    v_pos_4 = v_pos_4 + 1

                # ...within the web address, find the first  '/' after '//' if it exists
                v_pos_3 = v_note_text.find('/', v_pos_2)
                if (v_pos_3 < 0) or (v_pos_3 > v_pos_4):
                    v_pos_3 = v_pos_4

                v_full_web_address = v_note_text[v_pos_1:v_pos_4]
                v_short_web_address = v_note_text[v_pos_2:v_pos_3]  # "<WebLink>"

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
            hkSupportFunctions.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.70\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)
        else:
            # Portrait
            hkSupportFunctions.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.50\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)

        # End the minipage
        p_level.append(pl.NoEscape(r'\end{minipage}'))
        p_level.append(pl.NoEscape(r'\vfill'))

    def __get_filtered_photo_list(self):
        v_photo_list = []

        v_person = self.__person__
        for vMediaItem in v_person.__media_base__:
            v_media_handle = vMediaItem[4]
            v_media_rect = vMediaItem[5]  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media = hkMedia.Media(v_media_handle, self.__cursor__)
            v_media_mime = v_media.__mime__
            v_tag_handle_list = v_media.__tag_base__

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in hkGrampsDb.get_tag_list(v_tag_handle_list, v_person.__tag_dictionary__)) and (c_photo in hkGrampsDb.get_tag_list(v_tag_handle_list, v_person.__tag_dictionary__)):
                    v_photo_list.append([v_media_handle, v_media_rect])

        return v_photo_list

    def __get_filtered_document_list(self):
        v_document_list = []

        v_person = self.__person__
        for vMediaItem in v_person.__media_base__:
            v_media_handle = vMediaItem[4]
            v_media_rect = vMediaItem[5]  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media = hkMedia.Media(v_media_handle, self.__cursor__)
            v_media_mime = v_media.__mime__
            v_tag_handle_list = v_media.__tag_base__

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in hkGrampsDb.get_tag_list(v_tag_handle_list, v_person.__tag_dictionary__)) and (c_document in hkGrampsDb.get_tag_list(v_tag_handle_list, v_person.__tag_dictionary__)):
                    v_document_list.append([v_media_handle, v_media_rect])

        return v_document_list

    def __get_filtered_note_list(self, p_note_handle_list):
        """
        Removes all notes from p_note_handle_list that are of type 'Citation' or that are tagged 'Source'
        """

        v_note_list = []

        v_person = self.__person__
        for v_note_handle in p_note_handle_list:
            v_note = hkNote.Note(v_note_handle, self.__cursor__)
            v_tag_handle_list = v_note.__note_tag_base__
            v_type = v_note.__note_type__

            if not (c_source in hkGrampsDb.get_tag_list(v_tag_handle_list, v_person.__tag_dictionary__)) and not (v_type == hkGrampsDb.c_note_citation):
                v_note_list.append(v_note_handle)

        return v_note_list

    def __write_life_sketch_section(self, p_level):
        """
        Create a section with Life Sketch
        
        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__

        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('life sketch', self.__language__), pLabel=False) as v_sub_level:
            # Create a story line
            v_life_sketch = ""

            # Check whether life stories already exist in the notes
            for v_note_handle in v_person.__note_base__:
                v_note = hkNote.Note(v_note_handle, self.__cursor__)
                v_note_text = v_note.__note_text__
                v_note_type = v_note.__note_type__
                if v_note_type == hkGrampsDb.c_note_person:  # PersonChapter Note
                    v_life_sketch = v_life_sketch + pu.escape_latex(v_note_text)

            # If no specific life stories were found, then write one
            if len(v_life_sketch) == 0:
                v_full_name = v_person.__given_names__ + ' ' + v_person.__surname__
                v_he_she = hkLanguage.translate('He', self.__language__)
                v_his_her = hkLanguage.translate('His', self.__language__)
                v_brother_sister = hkLanguage.translate('Brother', self.__language__)
                v_father_mother = hkLanguage.translate('Father', self.__language__)
                if v_person.__gender__ == hkGrampsDb.c_gender_female:
                    v_he_she = hkLanguage.translate('She', self.__language__)
                    v_his_her = hkLanguage.translate('Her', self.__language__)
                    v_brother_sister = hkLanguage.translate('Sister', self.__language__)
                    v_father_mother = hkLanguage.translate('Mother', self.__language__)

                v_vital_event_keys = hkGrampsDb.c_vital_events_set.intersection(v_person.__person_event_dict__.keys())

                # Geboorte
                if hkGrampsDb.c_event_birth in v_vital_event_keys:  # Birth
                    for v_event in v_person.__person_event_dict__[hkGrampsDb.c_event_birth]:
                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        v_string = hkLanguage.translate("{0} was born on {1}", self.__language__).format(pu.escape_latex(v_full_name), v_date.__date_to_text__(False))
                        v_life_sketch = v_life_sketch + v_string

                        if v_place is not None:
                            v_string = hkLanguage.translate("in {0}", self.__language__).format(v_place.__place_to_text__(False))
                            v_life_sketch = v_life_sketch + ' ' + v_string

                        v_life_sketch = v_life_sketch + r". "

                # Baptism
                elif hkGrampsDb.c_event_baptism in v_vital_event_keys:
                    for v_event in v_person.__person_event_dict__[hkGrampsDb.c_event_baptism]:
                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        v_string = hkLanguage.translate("{0} was born about {1}", self.__language__).format(pu.escape_latex(v_full_name), v_date.__date_to_text__(False))
                        v_life_sketch = v_life_sketch + v_string

                        if v_place is not None:
                            v_string = hkLanguage.translate("in {0}", self.__language__).format(v_place.__place_to_text__(False))
                            v_life_sketch = v_life_sketch + ' ' + v_string

                        v_life_sketch = v_life_sketch + r". "

                # Roepnaam
                v_use_name = v_person.__given_names__
                if len(v_person.__call_name__) > 0:
                    v_use_name = v_person.__call_name__
                    v_string = hkLanguage.translate("{0} call name was {1}.", self.__language__).format(v_his_her, pu.escape_latex(v_use_name))
                    v_life_sketch = v_life_sketch + v_string

                if len(v_life_sketch) > 0:
                    v_life_sketch = v_life_sketch + r"\par "

                # Sisters and brothers
                v_number_sisters = 0
                v_number_brothers = 0
                v_sibling_names = []

                for v_sibling_handle in hkSupportFunctions.sort_person_list_by_birth(v_person.get_siblings(), self.__cursor__):
                    v_sibling = hkPerson.Person(v_sibling_handle, self.__cursor__)
                    if v_sibling.__gender__ == 0:
                        v_number_sisters = v_number_sisters + 1
                    elif v_sibling.__gender__ == 1:
                        v_number_brothers = v_number_brothers + 1

                    v_sibling_names.append(v_sibling.__given_names__)

                if v_number_sisters + v_number_brothers > 0:
                    v_string = ''
                    if v_number_sisters == 1 and v_number_brothers == 0:
                        v_string = hkLanguage.translate("{0} had one sister:", self.__language__).format(v_use_name)

                    if v_number_sisters > 1 and v_number_brothers == 0:
                        v_string = hkLanguage.translate("{0} had {1} sisters:", self.__language__).format(v_use_name, v_number_sisters)

                    if v_number_sisters == 0 and v_number_brothers == 1:
                        v_string = hkLanguage.translate("{0} had one brother:", self.__language__).format(v_use_name)

                    if v_number_sisters == 0 and v_number_brothers > 1:
                        v_string = hkLanguage.translate("{0} had {1} brothers:", self.__language__).format(v_use_name, v_number_brothers)

                    if v_number_sisters > 0 and v_number_brothers > 0:
                        v_string = hkLanguage.translate("{0} was {1} of", self.__language__).format(v_use_name, v_brother_sister.lower())

                    v_life_sketch = v_life_sketch + v_string + ' '

                    if len(v_sibling_names) > 1:
                        for vSiblingName in v_sibling_names[:-1]:
                            v_life_sketch = v_life_sketch + pu.escape_latex(vSiblingName) + ", "

                        v_life_sketch = v_life_sketch + hkLanguage.translate("and", self.__language__) + ' ' + pu.escape_latex(v_sibling_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "
                    elif len(v_sibling_names) == 1:
                        v_life_sketch = v_life_sketch + pu.escape_latex(v_sibling_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "

                # Partners and Children
                v_number_daughters = 0
                v_number_sons = 0
                v_child_names = []
                for v_child_handle in v_person.get_children():
                    v_child = hkPerson.Person(v_child_handle, self.__cursor__)
                    if v_child.__gender__ == 0:
                        v_number_daughters = v_number_daughters + 1
                    elif v_child.__gender__ == 1:
                        v_number_sons = v_number_sons + 1

                    v_child_names.append(v_child.__given_names__)

                if v_number_daughters + v_number_sons > 0:
                    v_string = ''
                    if v_number_daughters == 1 and v_number_sons == 0:
                        v_string = hkLanguage.translate("{0} had one daughter:", self.__language__).format(v_full_name)
                        if len(v_life_sketch) > 0:
                            v_string = hkLanguage.translate("Furthermore, {0} had one daughter:", self.__language__).format(v_use_name)

                    if v_number_daughters > 1 and v_number_sons == 0:
                        v_string = hkLanguage.translate("{0} had {1} daughters:", self.__language__).format(v_full_name, v_number_daughters)
                        if len(v_life_sketch) > 0:
                            v_string = hkLanguage.translate("Furthermore, {0} had {1} daughters:", self.__language__).format(v_use_name, v_number_daughters)

                    if v_number_daughters == 0 and v_number_sons == 1:
                        v_string = hkLanguage.translate("{0} had one son:", self.__language__).format(v_full_name)
                        if len(v_life_sketch) > 0:
                            v_string = hkLanguage.translate("Furthermore, {0} had one son:", self.__language__).format(v_use_name)

                    if v_number_daughters == 0 and v_number_sons > 1:
                        v_string = hkLanguage.translate("{0} had {1} sons:", self.__language__).format(v_full_name, v_number_sons)
                        if len(v_life_sketch) > 0:
                            v_string = hkLanguage.translate("Furthermore, {0} had {1} sons:", self.__language__).format(v_use_name, v_number_sons)

                    if v_number_daughters > 0 and v_number_sons > 0:
                        v_string = hkLanguage.translate("{0} was {1} of", self.__language__).format(v_full_name, v_father_mother.lower())
                        if len(v_life_sketch) > 0:
                            v_string = hkLanguage.translate("Furthermore, {0} was {1} of", self.__language__).format(v_use_name, v_father_mother.lower())

                    v_life_sketch = v_life_sketch + v_string + ' '

                    if len(v_child_names) > 1:
                        for v_child_name in v_child_names[:-1]:
                            v_life_sketch = v_life_sketch + pu.escape_latex(v_child_name) + ", "

                        v_life_sketch = v_life_sketch + hkLanguage.translate("and", self.__language__) + ' ' + pu.escape_latex(v_child_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "
                    elif len(v_child_names) == 1:
                        v_life_sketch = v_life_sketch + pu.escape_latex(v_child_names[-1]) + ". "
                        v_life_sketch = v_life_sketch + r"\par "

                # Death
                if hkGrampsDb.c_event_death in v_vital_event_keys:
                    for v_event in v_person.__person_event_dict__[hkGrampsDb.c_event_death]:
                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        v_string = hkLanguage.translate("{0} died on {1}", self.__language__).format(v_he_she, v_date.__date_to_text__(False))
                        v_life_sketch = v_life_sketch + v_string

                        if v_place is not None:
                            v_string = hkLanguage.translate("in {0}.", self.__language__).format(v_place.__place_to_text__(False))
                            v_life_sketch = v_life_sketch + ' ' + v_string
                        else:
                            v_life_sketch = v_life_sketch + ". "

                # Burial
                elif hkGrampsDb.c_event_burial in v_vital_event_keys:
                    for v_event in v_person.__person_event_dict__[hkGrampsDb.c_event_burial]:
                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        v_string = hkLanguage.translate("{0} died about {1}", self.__language__).format(v_he_she, v_date.__date_to_text__(False))
                        v_life_sketch = v_life_sketch + v_string

                        if v_place is not None:
                            v_string = hkLanguage.translate("and was buried in {0}.", self.__language__).format(v_place.__place_to_text__(False))
                            v_life_sketch = v_life_sketch + ' ' + v_string + ' '
                        else:
                            v_life_sketch = v_life_sketch + ". "

            v_life_sketch = v_life_sketch.replace(r"\n\n", r"\par")  # Replace double newline characters with \par
            v_life_sketch = v_life_sketch.replace(r"\newline\newline", r"par")  # Replace double newline characters with \par

            v_portrait_found = False
            for v_media_item in v_person.__media_base__:
                v_media_handle = v_media_item[4]
                v_media = hkMedia.Media(v_media_handle, self.__cursor__)
                if v_media.tag_name_in_media_tag_names('Portrait'):
                    v_portrait_found = True
                    hkSupportFunctions.wrap_figure(v_sub_level, p_filename=v_media.__media_path__, p_width=r'0.35\textwidth', p_text=v_life_sketch)

            if not v_portrait_found:
                v_sub_level.append(pl.NoEscape(v_life_sketch))

        v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_vital_information_section(self, p_level):
        """
        Create section with Vital Information

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('vital information', self.__language__), pLabel=False) as v_sub_level:
            with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                if len(v_person.__call_name__) > 0:
                    v_table.add_row([hkLanguage.translate('call name', self.__language__) + ":", v_person.__call_name__])

                if v_person.__gender__ in hkGrampsDb.c_gender_dict:
                    v_table.add_row([hkLanguage.translate('gender', self.__language__) + ":", hkLanguage.translate(hkGrampsDb.c_gender_dict[v_person.__gender__], self.__language__)])

                for v_event_key in v_person.__person_event_dict__.keys():
                    if v_event_key in hkGrampsDb.c_vital_events_set:
                        v_string_1 = "Date of " + hkGrampsDb.c_event_type_dict[v_event_key]
                        v_string_2 = "Place of " + hkGrampsDb.c_event_type_dict[v_event_key]

                        v_event_dict = v_person.__person_event_dict__[v_event_key]
                        for v_event in v_event_dict:
                            v_date = v_event.get_date()
                            v_place = v_event.get_place()

                            v_string3 = v_date.__date_to_text__(False)
                            v_string4 = v_place.__place_to_text__(False)

                            if len(v_string3) > 0:
                                v_table.add_row([hkLanguage.translate(v_string_1, self.__language__) + ":", v_string3])
                            if len(v_string4) > 0:
                                v_table.add_row([hkLanguage.translate(v_string_2, self.__language__) + ":", v_string4])

            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_parental_section_graph(self, p_level):
        """
        Creates a graphical family tree
        
        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__
        
        # Add Family graph
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('parental family', self.__language__), pLabel=False) as v_sub_level:
            # Create a sorted list of self and siblings
            v_sibling_list = v_person.get_siblings()
            v_sibling_list.append(v_person.__handle__)
            v_sibling_list = hkSupportFunctions.sort_person_list_by_birth(v_sibling_list, self.__cursor__)

            # Create nodes
            v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
            v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

            # Parents
            v_father_name = hkLanguage.translate('Unknown', self.__language__)
            if v_person.get_father() is not None:
                v_father = hkPerson.Person(v_person.get_father(), self.__cursor__)
                v_father_name = pl.NoEscape(hkLatex.GetPersonNameWithReference(v_father.__given_names__, v_father.__surname__, v_father.__gramps_id__))

            v_mother_name = hkLanguage.translate('Unknown', self.__language__)
            if v_person.get_mother() is not None:
                v_mother = hkPerson.Person(v_person.get_mother(), self.__cursor__)
                v_mother_name = pl.NoEscape(hkLatex.GetPersonNameWithReference(v_mother.__given_names__, v_mother.__surname__, v_mother.__gramps_id__))

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
                v_sibling = hkPerson.Person(v_sibling_handle, self.__cursor__)

                if v_sibling.__gramps_id__ == v_person.__gramps_id__:
                    v_sibling_name = v_person.__given_names__ + ' ' + v_person.__surname__
                else:
                    v_sibling_name = pl.NoEscape(hkLatex.GetPersonNameWithReference(v_sibling.__given_names__, v_sibling.__surname__, v_sibling.__gramps_id__))

                if v_sibling.__gender__ == 0:  # Female
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, woman'
                elif v_sibling.__gender__ == 1:  # Male
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man'
                else:
                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man'

                if v_sibling.__gramps_id__ == v_person.__gramps_id__:
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

    def __write_parental_section_table(self, p_level):
        """
        Creates a tabular family tree

        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__

        # Add Family table
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('parental family', self.__language__), pLabel=False) as vSubLevel:
            with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                v_father_name = hkLanguage.translate('Unknown', self.__language__)
                if v_person.get_father() is not None:
                    v_father = hkPerson.Person(v_person.get_father(), self.__cursor__)
                    v_father_name = pl.NoEscape(hkLatex.GetPersonNameWithReference(v_father.__given_names__, v_father.__surname__, v_father.__gramps_id__))

                v_table.add_row([hkLanguage.translate('father', self.__language__) + ":", v_father_name])

                v_mother_name = hkLanguage.translate('Unknown', self.__language__)
                if v_person.get_mother() is not None:
                    v_mother = hkPerson.Person(v_person.get_mother(), self.__cursor__)
                    v_mother_name = pl.NoEscape(hkLatex.GetPersonNameWithReference(v_mother.__given_names__, v_mother.__surname__, v_mother.__gramps_id__))

                v_table.add_row([hkLanguage.translate('mother', self.__language__) + ":", v_mother_name])

                for v_sibling_handle in hkSupportFunctions.sort_person_list_by_birth(v_person.get_siblings(), self.__cursor__):
                    v_sibling = hkPerson.Person(v_sibling_handle, self.__cursor__)
                    if v_sibling.__gramps_id__ == v_person.__gramps_id__:
                        v_sibling_type = hkLanguage.translate('self', self.__language__) + ":"
                    elif v_sibling.__gender__ == 0:
                        v_sibling_type = hkLanguage.translate('sister', self.__language__) + ":"
                    elif v_sibling.__gender__ == 1:
                        v_sibling_type = hkLanguage.translate('brother', self.__language__) + ":"
                    else:
                        v_sibling_type = hkLanguage.translate('unknown', self.__language__) + ":"

                    v_table.add_row([v_sibling_type, pl.NoEscape(hkLatex.GetPersonNameWithReference(v_sibling.__given_names__, v_sibling.__surname__, v_sibling.__gramps_id__))])

            vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_partner_sections_graph(self, p_level):
        """
        Creates a graphical family tree

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Add families with partners
        for v_family_handle in v_person.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)

            v_partner_handle = v_family.get_mother()
            if v_person.__gender__ == hkGrampsDb.c_gender_female:
                v_partner_handle = v_family.get_father()

            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner = hkPerson.Person(v_partner_handle, self.__cursor__)

                # For each partner create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=pl.NoEscape(hkLatex.GetPersonNameWithReference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)), pLabel=False) as vSubLevel:
                    v_family_event_dict: dict[str, list[hkEvent.Event]] = {}

                    # Create a family event dictionary
                    for v_family_event_ref in v_family.__event_ref_list__:
                        v_event = hkEventRef.EventRef(v_family_event_ref, self.__cursor__).get_event()

                        if v_event.get_type() in v_family_event_dict:
                            v_family_event_dict[v_event.get_type()].append(v_event)
                        else:
                            v_family_event_dict[v_event.get_type()] = [v_event]

                    # TODO: Sort family events on date

                    v_family_event_keys = hkGrampsDb.c_family_events_set.intersection(v_family_event_dict.keys())
                    if len(v_family_event_keys) > 0:
                        with hkLatex.CreateSubLevel(pLevel=vSubLevel, pTitle=hkLanguage.translate('family events', self.__language__), pLabel=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_event_key in v_family_event_keys:
                                    for v_event in v_family_event_dict[v_event_key]:
                                        v_date: hkDate.Date = v_event.get_date()
                                        v_place: hkPlace.Place = v_event.get_place()

                                        v_string_1 = "Date of " + hkGrampsDb.c_event_type_dict[v_event_key]
                                        v_string_2 = "Place of " + hkGrampsDb.c_event_type_dict[v_event_key]
                                        v_string_3 = v_date.get_start_date_text(False)
                                        v_string_4 = v_place.__place_to_text__(True)

                                        if len(v_string_3) > 0:
                                            v_table.add_row([hkLanguage.translate(v_string_1, self.__language__) + ":", v_string_3])
                                        if len(v_string_4) > 0:
                                            v_table.add_row([hkLanguage.translate(v_string_2, self.__language__) + ":", v_string_4])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                    # Add subchapter for children
                    if len(v_family.__child_ref_list__) > 0:
                        # If children exist, then create subchapter and a table
                        with hkLatex.CreateSubLevel(pLevel=vSubLevel, pTitle=hkLanguage.translate('children', self.__language__), pLabel=False) as v_sub_sub_level:
                            v_sub_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                            v_sub_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                            v_father_string = r'\node (father) [left, man, self] {\small ' + pl.NoEscape(v_person.__given_names__ + ' ' + v_person.__surname__) + r'};'
                            v_mother_string = r'\node (mother) [right, woman] {\small ' + pl.NoEscape(hkLatex.GetPersonNameWithReference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)) + r'};'
                            if v_person.__gender__ == hkGrampsDb.c_gender_female:
                                v_father_string = r'\node (father) [left, man] {\small ' + pl.NoEscape(hkLatex.GetPersonNameWithReference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)) + r'};'
                                v_mother_string = r'\node (mother) [right, woman, self] {\small ' + pl.NoEscape(v_person.__given_names__ + ' ' + v_person.__surname__) + r'};'

                            # First row
                            v_sub_sub_level.append(pu.NoEscape(v_father_string + r' &'))
                            v_sub_sub_level.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
                            v_sub_sub_level.append(pu.NoEscape(v_mother_string + r' \\'))

                            # Empty row
                            v_sub_sub_level.append(pu.NoEscape(r' & & \\'))

                            # Next one row per child
                            v_counter = 0
                            for v_reference in v_family.__child_ref_list__:
                                v_child_ref = hkPersonRef.PersonRef(v_reference, self.__cursor__)
                                v_counter = v_counter + 1
                                v_child = v_child_ref.get_person()

                                if v_child.__gender__ == hkGrampsDb.c_gender_female:
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, woman] {\small ' + pl.NoEscape(hkLatex.GetPersonNameWithReference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'
                                elif v_child.__gender__ == hkGrampsDb.c_gender_male:  # Male
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + pl.NoEscape(hkLatex.GetPersonNameWithReference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'
                                else:
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + pl.NoEscape(hkLatex.GetPersonNameWithReference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'

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
        """
        Creates a tabular family tree

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Add families with partners
        for v_family_handle in v_person.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)

            v_partner_handle = v_family.get_mother()
            if v_person.__gender__ == hkGrampsDb.c_gender_female:
                v_partner_handle = v_family.get_father()

            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner = hkPerson.Person(v_partner_handle, self.__cursor__)

                # For each partner create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=pl.NoEscape(hkLatex.GetPersonNameWithReference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)), pLabel=False) as vSubLevel:
                    v_family_event_dict: dict[str, list[hkEvent.Event]] = {}

                    # Create a family event dictionary
                    for v_family_event_ref in v_family.__event_ref_list__:
                        v_event = hkEventRef.EventRef(v_family_event_ref, self.__cursor__).get_event()

                        if v_event.get_type() in v_family_event_dict:
                            v_family_event_dict[v_event.get_type()].append(v_event)
                        else:
                            v_family_event_dict[v_event.get_type()] = [v_event]

                    # TODO: Sort family events on date

                    v_family_event_keys = hkGrampsDb.c_family_events_set.intersection(v_family_event_dict.keys())
                    if v_family_event_keys:
                        with hkLatex.CreateSubLevel(pLevel=vSubLevel, pTitle=hkLanguage.translate('family events', self.__language__), pLabel=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_event_key in v_family_event_keys:
                                    for v_event in v_family_event_dict[v_event_key]:
                                        v_date: hkDate.Date = v_event.get_date()
                                        v_place: hkPlace.Place = v_event.get_place()

                                        v_string_1 = "Date of " + hkGrampsDb.c_event_type_dict[v_event_key]
                                        v_string_2 = "Place of " + hkGrampsDb.c_event_type_dict[v_event_key]
                                        v_string_3 = v_date.get_start_date_text(False)
                                        v_string_4 = v_place.__place_to_text__(True)

                                        if len(v_string_3) > 0:
                                            v_table.add_row([hkLanguage.translate(v_string_1, self.__language__) + ":", v_string_3])
                                        if len(v_string_4) > 0:
                                            v_table.add_row([hkLanguage.translate(v_string_2, self.__language__) + ":", v_string_4])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                    # Add subchapter for children
                    if len(v_family.__child_ref_list__) > 0:
                        # If children exist, then create subchapter and a table
                        with hkLatex.CreateSubLevel(pLevel=vSubLevel, pTitle=hkLanguage.translate('children', self.__language__), pLabel=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_reference in v_family.__child_ref_list__:
                                    v_child_ref = hkPersonRef.PersonRef(v_reference, self.__cursor__)
                                    v_child = v_child_ref.get_person()

                                    if v_child.__gender__ == hkGrampsDb.c_gender_female:
                                        v_child_type = hkLanguage.translate('daughter', self.__language__) + ":"
                                    elif v_child.__gender__ == hkGrampsDb.c_gender_male:
                                        v_child_type = hkLanguage.translate('son', self.__language__) + ":"
                                    else:
                                        v_child_type = hkLanguage.translate('unknown', self.__language__) + ":"

                                    v_table.add_row([v_child_type, pl.NoEscape(hkLatex.GetPersonNameWithReference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__))])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_family_section(self, p_level):
        """
        Create a section listing all family relationships

        @param p_level: level of the chapter / section
        @return: None
        """

        # Create section with Family Information
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with p_level.create(hkLatex.Section(title=hkLanguage.translate('family', self.__language__), label=False)) as vSubLevel:
            self.__write_parental_section_graph(vSubLevel)
            self.__write_partner_sections_graph(vSubLevel)

    def __write_education_section(self, p_level):
        """
        Create a section with a table containing education

        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__

        # Create section with Education
        v_event_keys = hkGrampsDb.c_education_events_set.intersection(v_person.__person_event_dict__.keys())
        if v_event_keys:
            v_event_list = []
            for v_event_key in v_event_keys:
                v_event_list = v_event_list + v_person.__person_event_dict__[v_event_key]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('education', self.__language__), pLabel=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hkLanguage.translate('date', self.__language__)), pu.bold(hkLanguage.translate('course', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_event in v_event_list:
                        v_description = v_event.get_description()
                        if len(v_description) == 0:
                            v_description = '-'

                        v_date = v_event.get_date()
                        v_place = v_event.get_place()
                        v_table.add_row([v_date.__date_to_text__(True), pu.escape_latex(v_description) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_place.__place_to_text__())])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_profession_section(self, p_level):
        """
        Create a section with a table containing working experiences

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Create section with Working Experience ***
        v_event_keys = hkGrampsDb.c_professional_events_set.intersection(v_person.__person_event_dict__.keys())
        if v_event_keys:
            v_event_list = []
            for v_event_key in v_event_keys:
                v_event_list = v_event_list + v_person.__person_event_dict__[v_event_key]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('occupation', self.__language__), pLabel=False) as vSubLevel:
                with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hkLanguage.translate('date', self.__language__)), pu.bold(hkLanguage.translate('profession', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_event in v_event_list:
                        v_description = v_event.get_description()
                        if len(v_description) == 0:
                            v_description = '-'

                        v_date = v_event.get_date()
                        v_place = v_event.get_place()
                        v_table.add_row([v_date.__date_to_text__(True), pu.escape_latex(v_description) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_place.__place_to_text__())])

                vSubLevel.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_map(self, p_level):
        """
        Create a section with maps of all residences

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        #
        # Work in Progress
        #

        # Create section with Residential Information
        v_residential_events = hkGrampsDb.c_residential_events_set.intersection(v_person.__person_event_dict__.keys())
        if v_residential_events:
            # Create path name for map
            # v_path = self.__document_path + r'Figures'

            # Compose some temporary place type labels
            v_city_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_city]
            v_town_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_town]
            v_village_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_village]
            v_municipality_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_municipality]
            v_country_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_country]

            # Compose residence list
            v_residence_list = []
            for v_event in v_residential_events:
                v_residence_list = v_residence_list + v_person.__person_event_dict__[v_event]

            # Create minipage
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('residences', self.__language__), pLabel=False) as v_sub_level:
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

                    # 20220109: Limit number of maps to The Netherlands, Western Europe and the World
                    if v_country_code != 'NLD':
                        v_region_list = hkSupportFunctions.get_country_continent_subregion(v_country_code)
                        if v_region_list[1] == 'Western Europe':
                            v_country_code = 'WEU'
                        elif v_region_list[0] == 'Europe':
                            v_country_code = 'EUR'
                        else:
                            v_country_code = 'WLD'
                    
                    # Create path / file name for map
                    v_path = self.__document_path__ + r'Figures'
                    v_file_path = hkSupportFunctions.create_map(v_path, v_country_code)

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
                    v_coordinates = hkSupportFunctions.get_country_min_max_coordinates(v_country_code)
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

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Create section with Residential Information
        v_event_keys = hkGrampsDb.c_residential_events_set.intersection(v_person.__person_event_dict__.keys())
        if v_event_keys:
            v_event_list = []
            for v_event_key in v_event_keys:
                v_event_list = v_event_list + v_person.__person_event_dict__[v_event_key]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('residences', self.__language__), pLabel=False) as v_sub_level:
                # Create nodes
                v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                v_counter = 0
                for v_event in v_event_list:
                    v_counter = v_counter + 1

                    v_start_date = v_event.get_date().get_start_date_text()
                    v_address = v_event.get_place().__street_to_text__()

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

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Create section with Residential Information
        v_event_keys = hkGrampsDb.c_residential_events_set.intersection(v_person.__person_event_dict__.keys())
        if v_event_keys:
            v_event_list = []
            for v_event_key in v_event_keys:
                v_event_list = v_event_list + v_person.__person_event_dict__[v_event_key]

            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('residences', self.__language__), pLabel=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(hkLanguage.translate('date', self.__language__)), pu.bold(hkLanguage.translate('residence', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    for v_event in v_event_list:
                        v_date = v_event.get_date().__date_to_text__()
                        v_address = v_event.get_place().__street_to_text__()
                        v_table.add_row([v_date, pu.escape_latex(v_address)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_timeline_section(self, p_level):
        """
        Create section with timeline of life
        
        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        # TODO: Work in Progress

        def __add_to_timeline(p_person_handle, p_timeline_events, p_birth_date, p_death_date):
            v_person = hkPerson.Person(p_person_handle, self.__cursor__)
            for v_event_key in v_person.__person_event_dict__:
                if v_event_key in hkGrampsDb.c_vital_events_set:
                    for v_event in v_person.__person_event_dict__[v_event_key]:
                        v_type = v_event.get_type()
                        v_date = v_event.get_date()

                        if isinstance(v_date, list):  # TODO: Check if we do not omit too much data sets...
                            # Only include events that happen during the lifetime of the main person
                            # v_date_time = datetime.date(v_date[3], v_date[2], v_date[1])
                            v_date_time = hkSupportFunctions.gramps_date_to_python_date(v_date[1:4])  # TODO: Replcae by object method
                            if (p_birth_date is None) or (v_date_time > p_birth_date):
                                if (p_death_date is None) or (v_date_time < p_death_date):
                                    v_place = v_event.get_place()
                                    v_description = v_event.__description__
                                    if len(v_description) == 0:
                                        v_description = hkLanguage.translate(hkGrampsDb.c_event_type_dict[v_type]) + ' ' + v_person.__given_names__ + ' ' + v_person.__surname__

                                    v_list = [v_date, v_type, v_place, v_description]
                                    if p_timeline_events is None:
                                        p_timeline_events = [v_list]
                                    else:
                                        p_timeline_events.append(v_list)

        def __date_to_timeline(p_date, p_timeline_start_date, p_timeline_end_date, p_length_timeline=20):
            v_distance = (p_date - p_timeline_start_date) * p_length_timeline / (p_timeline_end_date - p_timeline_start_date)

            return v_distance

        def __calculate_start_end_dates(p_birth_date, p_death_date):
            if p_birth_date is None:
                if p_death_date is None:
                    v_start_date = datetime.date(datetime.date.today().year, 1, 1)
                else:
                    v_start_date = datetime.date(p_death_date.year - 100, 1, 1)
            else:
                v_start_date = datetime.date(p_birth_date.year, 1, 1)

            if p_death_date is None:
                v_end_date = datetime.date(v_start_date.year + 100, 1, 1)
            else:
                v_end_date = datetime.date(p_death_date.year + 1, 1, 1)

            v_today = datetime.date.today()
            if v_end_date > v_today:
                v_end_date = datetime.date(v_today.year + 1, 1, 1)

            # Round down / up to decennia
            v_start_date = datetime.date(int(hkSupportFunctions.round_down(v_start_date.year, -1)), 1, 1)
            v_end_date = datetime.date(int(hkSupportFunctions.round_up(v_end_date.year, -1)), 1, 1)

            return v_start_date, v_end_date

        # Initialise variables
        v_person = self.__person__

        v_timeline_events = []

        v_birth_date = None
        v_death_date = None

        # Copy the vital and residence events from the personal events dictionary
        for v_event_key in v_person.__person_event_dict__:
            if (v_event_key in hkGrampsDb.c_vital_events_set) or (v_event_key in hkGrampsDb.c_residential_events_set):
                for v_event in v_person.__person_event_dict__[v_event_key]:
                    v_type = v_event.get_type()
                    v_date = v_event.get_date()
                    v_place = v_event.get_place()
                    v_description = v_event.__description__
                    if len(v_description) == 0:
                        v_description = hkLanguage.translate(hkGrampsDb.c_event_type_dict[v_type]) + ' ' + v_person.__given_names__ + ' ' + v_person.__surname__

                    # Store birth / baptism and death / burial separately for later comparison
                    if v_type == hkGrampsDb.c_event_birth:
                        v_birth_date = v_date
                    elif v_type == hkGrampsDb.c_event_baptism and v_birth_date is None:
                        v_birth_date = v_date
                    elif v_type == hkGrampsDb.c_event_death:
                        v_death_date = v_date
                    elif v_type == hkGrampsDb.c_event_burial and v_death_date is None:
                        v_death_date = v_date

                    # Add event to list
                    v_list = [v_date, v_type, v_place, v_description]
                    if v_timeline_events is None:
                        v_timeline_events = [v_list]
                    else:
                        v_timeline_events.append(v_list)

        # Merge the family events
        for v_event_key in v_person.__family_event_dict__:
            v_type = v_event_key
            for v_event in v_person.__family_event_dict__[v_event_key]:
                v_date = v_event[0]
                v_place = v_event[1]
                v_description = v_event[2]
                if len(v_description) == 0:
                    v_description = hkLanguage.translate(hkGrampsDb.c_event_type_dict[v_type])  # TODO: extent with partner name

                v_list = [v_date, v_type, v_place, v_description]
                if v_timeline_events is None:
                    v_timeline_events = [v_list]
                else:
                    v_timeline_events.append(v_list)

        # Merge the vital information of partners
        for v_partner_handle in v_person.get_partners():
            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                __add_to_timeline(v_partner_handle, v_timeline_events, v_birth_date, v_death_date)

        # Merge the vital information of children
        for v_child_handle in v_person.get_children():
            if v_child_handle is not None:
                __add_to_timeline(v_child_handle, v_timeline_events, v_birth_date, v_death_date)

        # Sort the list
        f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
        v_timeline_events.sort(key=f_date_func)

        # Determine the start and end dates for the timeline
        v_start_date, v_end_date = __calculate_start_end_dates(v_birth_date, v_death_date)

        # Create the timeline section
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate('Timeline', self.__language__), pLabel=False) as v_sub_level:
            # Create nodes
            v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))

            # Define style
            v_sub_level.append(pu.NoEscape(r'[eventmarker/.style = {circle, draw = red!50, fill = red!20, thick, inner sep = 0 pt, minimum size = 5 pt},'))
            v_sub_level.append(pu.NoEscape(r'eventlabel/.style = {},'))
            v_sub_level.append(pu.NoEscape(r'residencemarker/.style = {circle, draw = green!50, fill = green!20, thick, inner sep = 0 pt, minimum size = 5 pt},'))
            v_sub_level.append(pu.NoEscape(r'residencelink/.style = {draw = green!50},'))
            v_sub_level.append(pu.NoEscape(r'residencelabel/.style = {},'))
            v_sub_level.append(pu.NoEscape(r'nostyle/.style = {}]'))

            # Draw the major timeline
            v_start_point = __date_to_timeline(v_start_date, v_start_date, v_end_date)
            v_end_point = __date_to_timeline(v_end_date, v_start_date, v_end_date)
            v_sub_level.append(pu.NoEscape(r'\draw[->, very thick] (0cm, ' + str(v_start_point) + r'cm) -- (0cm, ' + str(v_end_point) + r'cm);'))

            # Draw the decennial tick lines and display the year label
            v_string = str(v_start_point) + r'/' + str(v_start_date.year)
            for v_year in range(v_start_date.year + 10, v_end_date.year, 10):
                v_date = datetime.date(v_year, 1, 1)
                v_date_point = __date_to_timeline(v_date, v_start_date, v_end_date)
                v_string = v_string + r',' + str(v_date_point) + r'/' + str(v_year)

            v_sub_level.append(pu.NoEscape(r'\foreach \y/\ytext in {' + v_string + r'}'))
            v_sub_level.append(pu.NoEscape(r'\draw[thick, yshift =\y cm] (-2pt, 0pt) - - (2pt, 0pt) node[left=2pt] {$\ytext$};'))

            # Draw the events in the timeline
            v_count = 0
            for v_event in v_timeline_events:
                v_date_label = hkSupportFunctions.date_to_text(v_event[0])  # TODO: change to object method call
                v_type = v_event[1]
                v_place = hkSupportFunctions.street_to_text(v_event[2])  # TODO: change to object method call
                v_description = v_event[3]

                if v_type in hkGrampsDb.c_residential_events_set:
                    # Residence to the left
                    if len(v_event[0]) == 4:  # Single date events
                        v_date_1 = hkSupportFunctions.gramps_date_to_python_date(v_event[0][1:4])  # TODO: Replcae by object method
                        v_date_point_1 = __date_to_timeline(v_date_1, v_start_date, v_end_date)

                        v_count = v_count + 1
                        v_marker_name_1 = r'marker_' + str(v_count)
                        v_label_name_1 = r'label_' + str(v_count)

                        v_label = v_place + r'\\' + v_date_label
                        v_sub_level.append(pu.NoEscape(r'\node [residencemarker] (' + v_marker_name_1 + r') at (0 cm,' + str(v_date_point_1) + r' cm) {};'))
                        # v_sub_level.append(pu.NoEscape(r'\node [residencelabel] (' + v_label_name_1 + r') at (-2 cm,' + str(v_date_point_1) + r' cm) [label={[align=right, rotate=0]left:' + v_label + r'}] {};'))
                        v_sub_level.append(pu.NoEscape(r'\node [residencelabel, left=of ' + v_marker_name_1 + r', align=right, text width=5cm] (' + v_label_name_1 + r') at (-2 cm,' + str(v_date_point_1) + r' cm) {' + v_label + r'};'))
                        v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_1 + r'.west) -- (' + v_label_name_1 + r'.east);'))
                    elif len(v_event[0]) == 7:  # Dual date events
                        v_date_1 = hkSupportFunctions.gramps_date_to_python_date(v_event[0][1:4])  # TODO: Replcae by object method
                        v_date_2 = hkSupportFunctions.gramps_date_to_python_date(v_event[0][4:7])  # TODO: Replcae by object method

                        v_date_point_1 = __date_to_timeline(v_date_1, v_start_date, v_end_date)
                        v_date_point_2 = __date_to_timeline(v_date_2, v_start_date, v_end_date)
                        v_date_point_3 = (v_date_point_1 + v_date_point_2) / 2

                        v_count = v_count + 1
                        v_marker_name_1 = r'marker_' + str(v_count)

                        v_count = v_count + 1
                        v_marker_name_2 = r'marker_' + str(v_count)

                        v_count = v_count + 1
                        v_marker_name_3 = r'marker_' + str(v_count)

                        v_count = v_count + 1
                        v_marker_name_4 = r'marker_' + str(v_count)

                        v_label_name = r'label_' + str(v_count)

                        v_label = v_place + r'\\' + v_date_label
                        v_sub_level.append(pu.NoEscape(r'\node [residencemarker] (' + v_marker_name_1 + r') at (0 cm,' + str(v_date_point_1) + r' cm) {};'))
                        v_sub_level.append(pu.NoEscape(r'\node [residencemarker] (' + v_marker_name_2 + r') at (0 cm,' + str(v_date_point_2) + r' cm) {};'))
                        v_sub_level.append(pu.NoEscape(r'\coordinate (' + v_marker_name_3 + r') at (-2 cm,' + str(v_date_point_1) + r' cm + 3pt) {};'))
                        v_sub_level.append(pu.NoEscape(r'\coordinate (' + v_marker_name_4 + r') at (-2 cm,' + str(v_date_point_2) + r' cm - 3pt) {};'))

                        v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_1 + r'.west) -- (' + v_marker_name_3 + r');'))
                        v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_2 + r'.west) -- (' + v_marker_name_4 + r');'))
                        v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_3 + r') -- (' + v_marker_name_4 + r');'))

                        v_sub_level.append(pu.NoEscape(r'\node [residencelabel, left=of ' + v_marker_name_1 + r', align=right, text width=5cm] (' + v_label_name + r') at (-2 cm,' + str(v_date_point_3) + r' cm) {' + v_label + r'};'))
                else:
                    # Life events to the right
                    if len(v_event[0]) == 4:  # Single date events
                        v_date_1 = hkSupportFunctions.gramps_date_to_python_date(v_event[0][1:4])  # TODO: Replcae by object method
                        v_date_point_1 = __date_to_timeline(v_date_1, v_start_date, v_end_date)

                        v_count = v_count + 1
                        v_marker_name_1 = r'marker_' + str(v_count)
                        v_label_name_1 = r'label_' + str(v_count)

                        v_label = v_description + r'\\' + v_date_label + r', ' + v_place
                        v_sub_level.append(pu.NoEscape(r'\node [eventmarker] (' + v_marker_name_1 + r') at (0 cm,' + str(v_date_point_1) + r' cm) {};'))
                        v_sub_level.append(pu.NoEscape(r'\node [eventlabel, right=of ' + v_marker_name_1 + r', align=left, text width=5cm] (' + v_label_name_1 + r') at (1 cm,' + str(v_date_point_1) + r' cm) {' + v_label + r'};'))
                        v_sub_level.append(pu.NoEscape(r'\draw (' + v_marker_name_1 + r'.east) -- (' + v_label_name_1 + r'.west);'))

            v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_photo_section(self, p_level):
        """
        Create section with photos

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        v_filtered_list = self.__get_filtered_photo_list()
        if len(v_filtered_list) > 0:
            self.__write_media_section(p_level, v_filtered_list, p_title="photos")

    def __write_document_section(self, p_level):
        """
        Create section with document scans

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        v_filtered_list = self.__get_filtered_document_list()
        if len(v_filtered_list) > 0:
            self.__write_media_section(p_level, v_filtered_list, p_title='documents')

    def __write_media_section(self, p_level, p_filtered_list, p_title='media'):
        """
        Create section with media

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        # Allocate variables
        v_media_path_1 = None
        v_media_title_1 = None
        v_media_rect_1 = None
        v_media_path_2 = None
        v_media_title_2 = None
        v_media_rect_2 = None

        # Debug
        logging.debug("p_filtered_list: ".join(map(str, p_filtered_list)))

        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with hkLatex.CreateSubLevel(pLevel=p_level, pTitle=hkLanguage.translate(p_title, self.__language__), pLabel=False) as v_sub_level:
            #
            # 1. All media with notes
            #
            v_position = 'o'
            v_temp_list = p_filtered_list.copy()  # Use temporary list, so items can be removed while iterating
            for v_item in v_temp_list:
                v_media_handle = v_item[0]
                v_media_rect = v_item[1]

                v_media = hkMedia.Media(v_media_handle, self.__cursor__)
                v_media_path = v_media.__media_path__
                v_media_title = v_media.__description__
                v_media_note_handles = self.__get_filtered_note_list(v_media.__note_base__)

                # TODO: dit gaat mis als het om een note met tag 'source' gaat
                if len(v_media_note_handles) > 0:
                    # Media contains notes
                    v_position = 'o' if v_position == 'i' else 'i'  # Alternate position of image / text
                    self.__document_with_note(v_sub_level, v_media_path, v_media_title, v_media_note_handles, v_media_rect, v_position)  # 20220322: Added v_media_rect

                    # Done, remove from list
                    p_filtered_list.remove(v_item)

            #
            # 2. Remaining media, side by side
            #
            v_counter = 0

            v_temp_list = p_filtered_list.copy()  # Use temporary list, so items can be removed while iterating
            for v_item in v_temp_list:
                v_media_handle = v_item[0]
                v_media_rect = v_item[1]

                v_media = hkMedia.Media(v_media_handle, self.__cursor__)

                v_counter = v_counter + 1
                if v_counter % 2 == 1:
                    v_media_path_1 = v_media.__media_path__
                    v_media_title_1 = v_media.__description__
                    v_media_rect_1 = v_media_rect

                    # Remove media_1 from list
                    p_filtered_list.remove(v_item)
                else:
                    v_media_path_2 = v_media.__media_path__
                    v_media_title_2 = v_media.__description__
                    v_media_rect_2 = v_media_rect

                    hkSupportFunctions.picture_side_by_side_equal_height(v_sub_level, v_media_path_1, v_media_path_2, v_media_title_1, v_media_title_2, v_media_rect_1, v_media_rect_2)

                    # Remove media_2 from list
                    p_filtered_list.remove(v_item)

                    # Reset variables
                    v_media_path_1 = None
                    v_media_title_1 = None
                    v_media_rect_1 = None

                    v_media_path_2 = None
                    v_media_title_2 = None
                    v_media_rect_2 = None

            #
            # 3. In case temp list had an odd length, one media might be remaining
            #
            if v_media_path_1 is not None:
                # Latex Debug
                v_sub_level.append(pl.NoEscape("% hkPersonChapter.PersonChapter.__WriteMediaSection"))

                # 20230313: Start a minipage
                p_level.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

                if v_media_rect_1 is not None:
                    # 20220328: Set focus area
                    v_left_1 = '{' + str(v_media_rect_1[0] / 100) + r'\wd1}'
                    v_right_1 = '{' + str(1 - v_media_rect_1[2] / 100) + r'\wd1}'
                    v_top_1 = '{' + str(v_media_rect_1[1] / 100) + r'\ht1}'
                    v_bottom_1 = '{' + str(1 - v_media_rect[3] / 100) + r'\ht1}'

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

                    # with v_sub_level.create(hkLatex.Figure(position='htpb')) as vPhoto:
                    #     vPhoto.add_image(pl.NoEscape(v_media_path_1))
                    #     vPhoto.add_caption(pu.escape_latex(v_media_title_1))

                # 20230313: End the minipage
                p_level.append(pl.NoEscape(r'\end{minipage}'))

            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def write_person_chapter(self):
        """
        Writes the person to a separate chapter in a subdocument

        @param: None
        @return: None
        """

        v_person = self.__person__

        # Display progress
        print("Writing a chapter about: ", v_person.__given_names__, v_person.__surname__)

        # Create a new chapter for the active person
        v_chapter = hkLatex.Chapter(title=v_person.__given_names__ + ' ' + v_person.__surname__, label=v_person.__gramps_id__)

        self.__write_life_sketch_section(v_chapter)
        self.__write_vital_information_section(v_chapter)
        # self.__WriteFamilySection(v_chapter)
        self.__write_parental_section_graph(v_chapter)
        # self.__write_parental_section_table(v_chapter)
        self.__write_partner_sections_graph(v_chapter)
        self.__write_partner_sections_table(v_chapter)
        self.__write_education_section(v_chapter)
        self.__write_profession_section(v_chapter)
        self.__write_residence_section_timeline(v_chapter)
        self.__write_residence_section_table(v_chapter)
        # self.__WriteResidenceSection_Map(v_chapter)
        self.__write_photo_section(v_chapter)
        self.__write_document_section(v_chapter)
        # self.__write_timeline_section(v_chapter)

        v_chapter.generate_tex(filepath=self.__document_path__ + v_person.__gramps_id__)
