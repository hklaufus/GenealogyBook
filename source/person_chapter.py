import datetime
import logging
import numpy
import math
import os

import date
import event
import event_ref
import family
import media_ref
import note
import person
import person_ref
import place

import gramps_db
import language
import latex
import support_functions

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

    __cursor__ = None
    __chapter_path__: str = None
    __figures_path__: str = None
    __life_sketch_path__: str = None
    __language__: str = None

    def __init__(self, p_person_handle: str, p_cursor, p_chapter_path: str=None, p_figures_path: str=None, p_life_sketch_path: str=None, p_language: str='nl'):
        self.__cursor__ = p_cursor
        self.__chapter_path__ = p_chapter_path
        self.__figures_path__ = p_figures_path
        self.__life_sketch_path__ = p_life_sketch_path
        self.__language__ = p_language

        # Get basic person data
        self.__person__ = person.Person(p_person_handle, p_cursor)

    def __picture_with_note(self, p_level, p_image_path: str, p_image_title: str, p_image_notes: list[note.Note], p_image_rect=None, p_position: str='i'):
        """
        Adds a relevant personal picture including comments to the section

        :param p_level:
        :param p_image_path:
        :param p_image_title:
        :param p_image_notes:
        :param p_image_rect:
        :param p_position:
        :return:
        """

        # Latex Debug
        p_level.append(pl.NoEscape("% hkPersonChapter.PersonChapter.__picture_with_note"))

        self.__document_with_note(p_level, p_image_path, p_image_title, p_image_notes, p_image_rect, p_position)

    def __document_with_note(self, p_level, p_image_path: str, p_image_title: str, p_image_notes: list[note.Note], p_image_rect=None, p_position: str='i'):
        """
        Adds a relevant personal document including comments to the section

        :param p_level:
        :param p_image_path:
        :param p_image_title:
        :param p_image_notes:
        :param p_image_rect:
        :param p_position:
        :return:
        """

        # Add note(s)
        v_note_text: str = ''
        for v_note in p_image_notes:
            v_note_text = v_note.get_text()

            v_pos_1 = v_note_text.find("http")
            # Check whether the note contains a web address
            if v_pos_1 >= 0:  # 202303113
                # ...it does, first find '//'..
                v_pos_2 = v_note_text.find('//')+2

                # ...find the end of the web address
                v_pos_4 = v_pos_2
                while (v_pos_4 < len(v_note_text)) and (v_note_text[v_pos_4] != ' '):
                    v_pos_4 = v_pos_4 + 1

                # ...within the web address, find the first '/' after '//' if it exists
                v_pos_3 = v_note_text.find('/', v_pos_2)
                if (v_pos_3 < 0) or (v_pos_3 > v_pos_4):
                    v_pos_3 = v_pos_4

                v_full_web_address = v_note_text[v_pos_1:v_pos_4]
                v_short_web_address = v_note_text[v_pos_2:v_pos_3]  # "<WebLink>"

                # Debug logging
                logging.debug(f"v_full_web_address: {v_full_web_address}")
                logging.debug(f"v_short_web_address: {v_short_web_address}")

                if v_pos_1 == 0:
                    # ...and create a link to the source...
                    v_note_text = r'Link to source: \href{' + v_full_web_address + '}{' + v_short_web_address + r'}' + r'\par '
                else:
                    # ...and create a link in the note...
                    v_note_text = v_note_text.replace(v_full_web_address, r'\href{' + v_full_web_address + '}{' + v_short_web_address + r'}' + r'\par ')
            else:
                v_note_text = v_note_text + r' \par '
#            vTagHandleList = v_note_data[6]

        # Check on portrait vs landscape
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
            support_functions.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.70\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)
        else:
            # Portrait
            support_functions.wrap_figure(p_level, p_filename=p_image_path, p_caption=p_image_title, p_position=p_position, p_width=r'0.50\textwidth', p_text=v_note_text, p_zoom_rect=p_image_rect)

        # End the minipage
        p_level.append(pl.NoEscape(r'\end{minipage}'))
        p_level.append(pl.NoEscape(r'\vfill'))

    def __get_filtered_photo_list(self):
        """
        Returns a list with handles of media that are tagged as photo and publishable

        :return:
        """

        v_photo_list: list[media_ref.MediaRef] = []

        v_person = self.__person__
        for v_media_ref in v_person.__media_list__:
            v_media_rect = v_media_ref.get_rect()  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media = v_media_ref.get_media()
            v_media_mime = v_media.__mime__
            v_tage_names = [v_tag.__tag_name__ for v_tag in v_media.__tag_list__]

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in v_tage_names) and (c_photo in v_tage_names):
                    # v_photo_list.append([v_media.__handle__, v_media_rect])
                    v_photo_list.append(v_media_ref)

        return v_photo_list

    def __get_filtered_document_list(self):
        v_document_list: list[media_ref.MediaRef] = []

        v_person = self.__person__
        for v_media_ref in v_person.__media_list__:
            v_media_rect = v_media_ref.get_rect()  # corner1 and corner 2 in Media Reference Editor in Gramps
            v_media = v_media_ref.get_media()
            v_media_mime = v_media.__mime__
            v_tage_names = [v_tag.__tag_name__ for v_tag in v_media.__tag_list__]

            if (v_media_mime.lower() == 'image/jpeg') or (v_media_mime.lower() == 'image/png'):
                if (c_publishable in v_tage_names) and (c_document in v_tage_names):
                    # v_document_list.append([v_media.__handle__, v_media_rect])
                    v_document_list.append(v_media_ref)

        return v_document_list

    def __get_filtered_note_list(self, p_note_list: list[note.Note]):
        """
        Removes all notes from p_note_handle_list that are of type 'Citation' or that are tagged 'Source'
        """

        v_note_list: list[note.Note] = []

        v_person = self.__person__
        for v_note in p_note_list:
            v_type = v_note.__note_type__.get_value()

            if not (c_source in gramps_db.get_tag_list(v_note.__note_tag_list__, v_person.__tag_dictionary__)) and not (v_type == gramps_db.c_note_citation):
                v_note_list.append(v_note)

        return v_note_list

    def __write_life_sketch_section(self, p_level):
        """
        Create a section with Life Sketch
        
        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__

        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('life sketch', self.__language__), p_label=False) as v_sub_level:
            v_found = False

            # Check whether life stories already exist in a latex file
            v_ls_filename = self.__life_sketch_path__ + r'LS_' + v_person.__gramps_id__ + r'.tex'
            if os.path.exists(v_ls_filename):
                v_sub_level.append(pl.NoEscape(r'\input{' + v_ls_filename + r'}'))
            else:
                # Create a story line
                v_life_sketch = ""
                if not v_found:
                    # Check whether life stories already exist in the notes
                    for v_note in v_person.__note_list__:
                        v_note_text = v_note.__note_text__
                        v_note_type = v_note.__note_type__
                        if v_note_type == gramps_db.c_note_person:  # PersonChapter Note
                            v_life_sketch = v_life_sketch + pu.escape_latex(v_note_text)
                            v_found = True

                if not v_found:
                    # If no specific life stories were found, then write one
                    v_full_name = v_person.__given_names__ + ' ' + v_person.__surname__
                    v_he_she = language.translate('He', self.__language__)
                    v_his_her = language.translate('His', self.__language__)
                    v_brother_sister = language.translate('Brother', self.__language__)
                    v_father_mother = language.translate('Father', self.__language__)
                    if v_person.__gender__ == gramps_db.c_gender_female:
                        v_he_she = language.translate('She', self.__language__)
                        v_his_her = language.translate('Her', self.__language__)
                        v_brother_sister = language.translate('Sister', self.__language__)
                        v_father_mother = language.translate('Mother', self.__language__)

                    # Geboorte
                    v_found = False
                    for v_event in v_person.get_events(gramps_db.c_event_birth):
                        v_found = True

                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        if v_date is not None:
                            v_string = language.translate("{0} was born on {1}", self.__language__).format(pu.escape_latex(v_full_name), v_date.__date_to_text__(False))
                            v_life_sketch = v_life_sketch + v_string

                            if v_place is not None:
                                v_string = language.translate("in {0}", self.__language__).format(v_place.__city_to_text__(False))
                                v_life_sketch = v_life_sketch + ' ' + v_string

                            v_life_sketch = v_life_sketch + r". "

                    # Baptism
                    if not v_found:
                        for v_event in v_person.get_events(gramps_db.c_event_baptism):
                            v_date = v_event.get_date()
                            v_place = v_event.get_place()

                            if v_date is not None:
                                v_string = language.translate("{0} was born about {1}", self.__language__).format(pu.escape_latex(v_full_name), v_date.__date_to_text__(False))
                                v_life_sketch = v_life_sketch + v_string

                                if v_place is not None:
                                    v_string = language.translate("in {0}", self.__language__).format(v_place.__city_to_text__(False))
                                    v_life_sketch = v_life_sketch + ' ' + v_string

                                v_life_sketch = v_life_sketch + r". "

                    # Roepnaam
                    v_use_name = v_person.__given_names__
                    if len(v_person.__call_name__) > 0:
                        v_use_name = v_person.__call_name__
                        v_string = language.translate("{0} call name was {1}.", self.__language__).format(v_his_her, pu.escape_latex(v_use_name))
                        v_life_sketch = v_life_sketch + v_string

                    if len(v_life_sketch) > 0:
                        v_life_sketch = v_life_sketch + r"\par "

                    # Sisters and brothers
                    v_number_sisters = 0
                    v_number_brothers = 0
                    v_sibling_names = []

                    for v_sibling_handle in support_functions.sort_person_list_by_birth(v_person.get_sibling_handles(), self.__cursor__):
                        v_sibling = person.Person(v_sibling_handle, self.__cursor__)
                        if v_sibling.__gender__ == 0:
                            v_number_sisters = v_number_sisters + 1
                        elif v_sibling.__gender__ == 1:
                            v_number_brothers = v_number_brothers + 1

                        v_sibling_names.append(v_sibling.__given_names__)

                    if v_number_sisters + v_number_brothers > 0:
                        v_string = ''
                        if v_number_sisters == 1 and v_number_brothers == 0:
                            v_string = language.translate("{0} had one sister:", self.__language__).format(v_use_name)

                        if v_number_sisters > 1 and v_number_brothers == 0:
                            v_string = language.translate("{0} had {1} sisters:", self.__language__).format(v_use_name, v_number_sisters)

                        if v_number_sisters == 0 and v_number_brothers == 1:
                            v_string = language.translate("{0} had one brother:", self.__language__).format(v_use_name)

                        if v_number_sisters == 0 and v_number_brothers > 1:
                            v_string = language.translate("{0} had {1} brothers:", self.__language__).format(v_use_name, v_number_brothers)

                        if v_number_sisters > 0 and v_number_brothers > 0:
                            v_string = language.translate("{0} was {1} of", self.__language__).format(v_use_name, v_brother_sister.lower())

                        v_life_sketch = v_life_sketch + v_string + ' '

                        if len(v_sibling_names) > 1:
                            for vSiblingName in v_sibling_names[:-1]:
                                v_life_sketch = v_life_sketch + pu.escape_latex(vSiblingName) + ", "

                            v_life_sketch = v_life_sketch + language.translate("and", self.__language__) + ' ' + pu.escape_latex(v_sibling_names[-1]) + ". "
                            v_life_sketch = v_life_sketch + r"\par "
                        elif len(v_sibling_names) == 1:
                            v_life_sketch = v_life_sketch + pu.escape_latex(v_sibling_names[-1]) + ". "
                            v_life_sketch = v_life_sketch + r"\par "

                    # Partners and Children
                    v_number_daughters: int = 0
                    v_number_sons: int = 0
                    v_child_names: list[str] = []

                    for v_child_handle in v_person.get_child_handles():
                        v_child = person.Person(v_child_handle, self.__cursor__)
                        if v_child.__gender__ == 0:
                            v_number_daughters = v_number_daughters + 1
                        elif v_child.__gender__ == 1:
                            v_number_sons = v_number_sons + 1

                        v_child_names.append(v_child.__given_names__)

                    if v_number_daughters + v_number_sons > 0:
                        v_string: str = ''

                        if v_number_daughters == 1 and v_number_sons == 0:
                            v_string = language.translate("{0} had one daughter:", self.__language__).format(v_full_name)
                            if len(v_life_sketch) > 0:
                                v_string = language.translate("Furthermore, {0} had one daughter:", self.__language__).format(v_use_name)

                        if v_number_daughters > 1 and v_number_sons == 0:
                            v_string = language.translate("{0} had {1} daughters:", self.__language__).format(v_full_name, v_number_daughters)
                            if len(v_life_sketch) > 0:
                                v_string = language.translate("Furthermore, {0} had {1} daughters:", self.__language__).format(v_use_name, v_number_daughters)

                        if v_number_daughters == 0 and v_number_sons == 1:
                            v_string = language.translate("{0} had one son:", self.__language__).format(v_full_name)
                            if len(v_life_sketch) > 0:
                                v_string = language.translate("Furthermore, {0} had one son:", self.__language__).format(v_use_name)

                        if v_number_daughters == 0 and v_number_sons > 1:
                            v_string = language.translate("{0} had {1} sons:", self.__language__).format(v_full_name, v_number_sons)
                            if len(v_life_sketch) > 0:
                                v_string = language.translate("Furthermore, {0} had {1} sons:", self.__language__).format(v_use_name, v_number_sons)

                        if v_number_daughters > 0 and v_number_sons > 0:
                            v_string = language.translate("{0} was {1} of", self.__language__).format(v_full_name, v_father_mother.lower())
                            if len(v_life_sketch) > 0:
                                v_string = language.translate("Furthermore, {0} was {1} of", self.__language__).format(v_use_name, v_father_mother.lower())

                        v_life_sketch = v_life_sketch + v_string + ' '

                        if len(v_child_names) > 1:
                            for v_child_name in v_child_names[:-1]:
                                v_life_sketch = v_life_sketch + pu.escape_latex(v_child_name) + ", "

                            v_life_sketch = v_life_sketch + language.translate("and", self.__language__) + ' ' + pu.escape_latex(v_child_names[-1]) + ". "
                            v_life_sketch = v_life_sketch + r"\par "
                        elif len(v_child_names) == 1:
                            v_life_sketch = v_life_sketch + pu.escape_latex(v_child_names[-1]) + ". "
                            v_life_sketch = v_life_sketch + r"\par "

                    # Death
                    v_found = False
                    for v_event in v_person.get_events(gramps_db.c_event_death):
                        v_found = True

                        v_date = v_event.get_date()
                        v_place = v_event.get_place()

                        if v_date is not None:
                            v_string = language.translate("{0} died on {1}", self.__language__).format(v_he_she, v_date.__date_to_text__(False))
                            v_life_sketch = v_life_sketch + v_string

                            if v_place is not None:
                                v_string = language.translate("in {0}.", self.__language__).format(v_place.__city_to_text__(False))
                                v_life_sketch = v_life_sketch + ' ' + v_string
                            else:
                                v_life_sketch = v_life_sketch + ". "

                    # Burial
                    if not v_found:
                        for v_event in v_person.get_events(gramps_db.c_event_burial):
                            v_date = v_event.get_date()
                            v_place = v_event.get_place()

                            if v_date is not None:
                                v_string = language.translate("{0} died about {1}", self.__language__).format(v_he_she, v_date.__date_to_text__(False))
                                v_life_sketch = v_life_sketch + v_string

                                if v_place is not None:
                                    v_string = language.translate("and was buried in {0}.", self.__language__).format(v_place.__city_to_text__(False))
                                    v_life_sketch = v_life_sketch + ' ' + v_string + ' '
                                else:
                                    v_life_sketch = v_life_sketch + ". "

                    v_life_sketch = v_life_sketch.replace(r"\n\n", r"\par")  # Replace double newline characters with \par
                    v_life_sketch = v_life_sketch.replace(r"\newline\newline", r"par")  # Replace double newline characters with \par

                v_portrait_found = False
                for v_media_ref in v_person.__media_list__:
                    v_media = v_media_ref.get_media()
                    if v_media.tag_name_in_media_tag_names('Portrait'):
                        v_portrait_found = True
                        support_functions.wrap_figure(v_sub_level, p_filename=v_media.__media_path__, p_width=r'0.35\textwidth', p_text=v_life_sketch)

                if not v_portrait_found:
                    v_sub_level.append(pl.NoEscape(v_life_sketch))

            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_vital_information_section(self, p_level):
        """
        Create a section with Vital Information

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('vital information', self.__language__), p_label=False) as v_sub_level:
            with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                if len(v_person.__call_name__) > 0:
                    v_table.add_row([language.translate('call name', self.__language__) + ":", v_person.__call_name__])

                if v_person.__gender__ in gramps_db.c_gender_dict:
                    v_table.add_row([language.translate('gender', self.__language__) + ":", language.translate(gramps_db.c_gender_dict[v_person.__gender__], self.__language__)])

                for v_event in v_person.get_events(gramps_db.c_vital_events_set):
                    v_type = v_event.get_type().get_value()
                    v_date = v_event.get_date()
                    v_place = v_event.get_place()

                    v_string_1 = "Date of " + gramps_db.c_event_type_dict[v_type]
                    v_string_2 = "Place of " + gramps_db.c_event_type_dict[v_type]

                    if v_date is not None:
                        v_string3 = v_date.__date_to_text__(False)
                        if len(v_string3) > 0:
                            v_table.add_row([language.translate(v_string_1, self.__language__) + ":", v_string3])

                    if v_place is not None:
                        v_string4 = v_place.__place_to_text__(True)
                        if len(v_string4) > 0:
                            v_table.add_row([language.translate(v_string_2, self.__language__) + ":", v_string4])

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
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('parental family', self.__language__), p_label=False) as v_sub_level:
            # Create a sorted list of self and siblings
            v_sibling_list = v_person.get_sibling_handles()
            v_sibling_list.append(v_person.__handle__)
            v_sibling_list = support_functions.sort_person_list_by_birth(v_sibling_list, self.__cursor__)

            # Create nodes
            v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
            v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

            # Parents
            v_father_name = language.translate('Unknown', self.__language__)
            if v_person.get_father_handle() is not None:
                v_father = person.Person(v_person.get_father_handle(), self.__cursor__)
                v_father_name = pl.NoEscape(latex.get_person_name_with_reference(v_father.__given_names__, v_father.__surname__, v_father.__gramps_id__))

            v_mother_name = language.translate('Unknown', self.__language__)
            if v_person.get_mother_handle() is not None:
                v_mother = person.Person(v_person.get_mother_handle(), self.__cursor__)
                v_mother_name = pl.NoEscape(latex.get_person_name_with_reference(v_mother.__given_names__, v_mother.__surname__, v_mother.__gramps_id__))

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
                v_sibling = person.Person(v_sibling_handle, self.__cursor__)

                if v_sibling.__gramps_id__ == v_person.__gramps_id__:
                    v_sibling_name = v_person.__given_names__ + ' ' + v_person.__surname__
                else:
                    v_sibling_name = pl.NoEscape(latex.get_person_name_with_reference(v_sibling.__given_names__, v_sibling.__surname__, v_sibling.__gramps_id__))

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
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('parental family', self.__language__), p_label=False) as vSubLevel:
            with vSubLevel.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                v_father_name = language.translate('Unknown', self.__language__)
                if v_person.get_father_handle() is not None:
                    v_father = person.Person(v_person.get_father_handle(), self.__cursor__)
                    v_father_name = pl.NoEscape(latex.get_person_name_with_reference(v_father.__given_names__, v_father.__surname__, v_father.__gramps_id__))

                v_table.add_row([language.translate('father', self.__language__) + ":", v_father_name])

                v_mother_name = language.translate('Unknown', self.__language__)
                if v_person.get_mother_handle() is not None:
                    v_mother = person.Person(v_person.get_mother_handle(), self.__cursor__)
                    v_mother_name = pl.NoEscape(latex.get_person_name_with_reference(v_mother.__given_names__, v_mother.__surname__, v_mother.__gramps_id__))

                v_table.add_row([language.translate('mother', self.__language__) + ":", v_mother_name])

                for v_sibling_handle in support_functions.sort_person_list_by_birth(v_person.get_sibling_handles(), self.__cursor__):
                    v_sibling = person.Person(v_sibling_handle, self.__cursor__)
                    if v_sibling.__gramps_id__ == v_person.__gramps_id__:
                        v_sibling_type = language.translate('self', self.__language__) + ":"
                    elif v_sibling.__gender__ == 0:
                        v_sibling_type = language.translate('sister', self.__language__) + ":"
                    elif v_sibling.__gender__ == 1:
                        v_sibling_type = language.translate('brother', self.__language__) + ":"
                    else:
                        v_sibling_type = language.translate('unknown', self.__language__) + ":"

                    v_table.add_row([v_sibling_type, pl.NoEscape(latex.get_person_name_with_reference(v_sibling.__given_names__, v_sibling.__surname__, v_sibling.__gramps_id__))])

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
            v_family = family.Family(v_family_handle, self.__cursor__)

            v_partner = v_family.get_mother()
            if v_person.__gender__ == gramps_db.c_gender_female:
                v_partner = v_family.get_father()

            if v_partner is not None:  # TODO: Also handle families with unknown partners
                # v_partner = person.Person(v_partner, self.__cursor__)

                # For each partner, create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with latex.create_sub_level(p_level=p_level, p_title=pl.NoEscape(latex.get_person_name_with_reference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)), p_label=False) as vSubLevel:
                    v_family_event_dict: dict[str, list[event.Event]] = {}

                    # Create a family event dictionary
                    for v_family_event_ref in v_family.__event_ref_list__:
                        # v_event = event_ref.EventRef(v_family_event_ref, self.__cursor__).get_event()
                        v_event = v_family_event_ref.get_event()

                        if v_event.get_type() in v_family_event_dict:
                            v_family_event_dict[v_event.get_type()].append(v_event)
                        else:
                            v_family_event_dict[v_event.get_type()] = [v_event]

                    # TODO: Sort family events on date

                    v_family_event_keys = gramps_db.c_family_events_set.intersection(v_family_event_dict.keys())
                    if len(v_family_event_keys) > 0:
                        with latex.create_sub_level(p_level=vSubLevel, p_title=language.translate('family events', self.__language__), p_label=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_event_key in v_family_event_keys:
                                    for v_event in v_family_event_dict[v_event_key]:
                                        v_date = v_event.get_date()
                                        v_place = v_event.get_place()

                                        v_string_1 = "Date of " + gramps_db.c_event_type_dict[v_event_key]
                                        v_string_2 = "Place of " + gramps_db.c_event_type_dict[v_event_key]

                                        if v_date is not None:
                                            v_string_3 = v_date.get_start_date_text(False)
                                            if len(v_string_3) > 0:
                                                v_table.add_row([language.translate(v_string_1, self.__language__) + ":", v_string_3])
                                        if v_place is not None:
                                            v_string_4 = v_place.__place_to_text__(True)
                                            if len(v_string_4) > 0:
                                                v_table.add_row([language.translate(v_string_2, self.__language__) + ":", v_string_4])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                    # Add subchapter for children
                    if len(v_family.__child_ref_list__) > 0:
                        # If children exist, then create subchapter and a table
                        with latex.create_sub_level(p_level=vSubLevel, p_title=language.translate('children', self.__language__), p_label=False) as v_sub_sub_level:
                            v_sub_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                            v_sub_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                            v_father_string = r'\node (father) [left, man, self] {\small ' + pl.NoEscape(v_person.__given_names__ + ' ' + v_person.__surname__) + r'};'
                            v_mother_string = r'\node (mother) [right, woman] {\small ' + pl.NoEscape(latex.get_person_name_with_reference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)) + r'};'
                            if v_person.__gender__ == gramps_db.c_gender_female:
                                v_father_string = r'\node (father) [left, man] {\small ' + pl.NoEscape(latex.get_person_name_with_reference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)) + r'};'
                                v_mother_string = r'\node (mother) [right, woman, self] {\small ' + pl.NoEscape(v_person.__given_names__ + ' ' + v_person.__surname__) + r'};'

                            # First row
                            v_sub_sub_level.append(pu.NoEscape(v_father_string + r' &'))
                            v_sub_sub_level.append(pu.NoEscape(r'\node (p0)     [terminal]     {+}; &'))
                            v_sub_sub_level.append(pu.NoEscape(v_mother_string + r' \\'))

                            # Empty row
                            v_sub_sub_level.append(pu.NoEscape(r' & & \\'))

                            # Next one row per child
                            v_counter = 0
                            for v_child_ref in v_family.__child_ref_list__:
                                # v_child_ref = person_ref.PersonRef(v_reference, self.__cursor__)
                                v_counter = v_counter + 1
                                v_child = v_child_ref.get_child()

                                if v_child.__gender__ == gramps_db.c_gender_female:
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, woman] {\small ' + pl.NoEscape(latex.get_person_name_with_reference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'
                                elif v_child.__gender__ == gramps_db.c_gender_male:  # Male
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + pl.NoEscape(latex.get_person_name_with_reference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'
                                else:
                                    v_string = r' & & \node (p' + str(v_counter) + r') [right, man] {\small ' + pl.NoEscape(latex.get_person_name_with_reference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__)) + r'}; \\'

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
            v_family = family.Family(v_family_handle, self.__cursor__)

            v_partner_handle = v_family.get_mother()
            if v_person.__gender__ == gramps_db.c_gender_female:
                v_partner_handle = v_family.get_father()

            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner = person.Person(v_partner_handle, self.__cursor__)

                # For each partner, create a subsection
                p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
                with latex.create_sub_level(p_level=p_level, p_title=pl.NoEscape(latex.get_person_name_with_reference(v_partner.__given_names__, v_partner.__surname__, v_partner.__gramps_id__)), p_label=False) as vSubLevel:
                    v_family_event_dict: dict[str, list[event.Event]] = {}

                    # Create a family event dictionary
                    for v_family_event_ref in v_family.__event_ref_list__:
                        v_event = event_ref.EventRef(v_family_event_ref, self.__cursor__).get_event()

                        if v_event.get_type() in v_family_event_dict:
                            v_family_event_dict[v_event.get_type()].append(v_event)
                        else:
                            v_family_event_dict[v_event.get_type()] = [v_event]

                    # TODO: Sort family events on date

                    v_family_event_keys = gramps_db.c_family_events_set.intersection(v_family_event_dict.keys())
                    if v_family_event_keys:
                        with latex.create_sub_level(p_level=vSubLevel, p_title=language.translate('family events', self.__language__), p_label=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_event_key in v_family_event_keys:
                                    for v_event in v_family_event_dict[v_event_key]:
                                        v_date: date.Date = v_event.get_date()
                                        v_place: place.Place = v_event.get_place()

                                        v_string_1 = "Date of " + gramps_db.c_event_type_dict[v_event_key]
                                        v_string_2 = "Place of " + gramps_db.c_event_type_dict[v_event_key]

                                        if v_date is not None:
                                            v_string_3 = v_date.get_start_date_text(False)
                                            if len(v_string_3) > 0:
                                                v_table.add_row([language.translate(v_string_1, self.__language__) + ":", v_string_3])
                                        if v_place is not None:
                                            v_string_4 = v_place.__place_to_text__(True)
                                            if len(v_string_4) > 0:
                                                v_table.add_row([language.translate(v_string_2, self.__language__) + ":", v_string_4])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

                    # Add subchapter for children
                    if len(v_family.__child_ref_list__) > 0:
                        # If children exist, then create subchapter and a table
                        with latex.create_sub_level(p_level=vSubLevel, p_title=language.translate('children', self.__language__), p_label=False) as v_sub_sub_level:
                            with v_sub_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                                for v_reference in v_family.__child_ref_list__:
                                    v_child_ref = person_ref.PersonRef(v_reference, self.__cursor__)
                                    v_child = v_child_ref.get_person()

                                    if v_child.__gender__ == gramps_db.c_gender_female:
                                        v_child_type = language.translate('daughter', self.__language__) + ":"
                                    elif v_child.__gender__ == gramps_db.c_gender_male:
                                        v_child_type = language.translate('son', self.__language__) + ":"
                                    else:
                                        v_child_type = language.translate('unknown', self.__language__) + ":"

                                    v_table.add_row([v_child_type, pl.NoEscape(latex.get_person_name_with_reference(v_child.__given_names__, v_child.__surname__, v_child.__gramps_id__))])

                            v_sub_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_family_section(self, p_level):
        """
        Create a section listing all family relationships

        @param p_level: level of the chapter / section
        @return: None
        """

        # Create a section with Family Information
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with p_level.create(latex.Section(title=language.translate('family', self.__language__), label=False)) as vSubLevel:
            self.__write_parental_section_graph(vSubLevel)
            self.__write_partner_sections_graph(vSubLevel)

    def __write_education_section(self, p_level):
        """
        Create a section with a table containing education

        @param p_level: level of the chapter / section
        @return: None
        """
        
        v_person = self.__person__

        # Create a temporary list and sort
        v_event_list = []
        for v_event in v_person.get_events(gramps_db.c_education_events_set):
            v_event_list.append(v_event)

        if len(v_event_list) > 0:
            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            # Create a section with Education
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with latex.create_sub_level(p_level=p_level, p_title=language.translate('education', self.__language__), p_label=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(language.translate('date', self.__language__)), pu.bold(language.translate('course', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_event in v_event_list:
                        v_description = v_event.get_description()
                        if len(v_description) == 0:
                            v_description = '-'

                        v_string_1 = ''
                        v_date = v_event.get_date()
                        if v_date is not None:
                            v_string_1 = v_date.__date_to_text__(True)

                        v_string_2 = ''
                        v_place = v_event.get_place()
                        if v_place is not None:
                            v_string_2 = v_place.__place_to_text__()

                        v_table.add_row([v_string_1, pu.escape_latex(v_description) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_string_2)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_profession_section(self, p_level):
        """
        Create a section with a table containing working experiences

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        # Create a temporary list and sort
        v_event_list = []
        for v_event in v_person.get_events(gramps_db.c_professional_events_set):
            v_event_list.append(v_event)

        if len(v_event_list) > 0:
            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            # Create a section with Working Experience
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with latex.create_sub_level(p_level=p_level, p_title=language.translate('occupation', self.__language__), p_label=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(language.translate('date', self.__language__)), pu.bold(language.translate('profession', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    # Add row for each event
                    for v_event in v_event_list:
                        v_description = v_event.get_description()
                        if len(v_description) == 0:
                            v_description = '-'

                        v_string_1 = ''
                        v_date = v_event.get_date()
                        if v_date is not None:
                            v_string_1 = v_date.__date_to_text__(True)

                        v_string_2 = ''
                        v_place = v_event.get_place()
                        if v_place is not None:
                            v_string_2 = v_place.__street_to_text__(True)
                            if len(v_string_2) > 0:
                                v_string_2 = v_string_2 + ", " + v_place.__city_to_text__()
                            else:
                                v_string_2 = v_place.__city_to_text__()

                        v_table.add_row([v_string_1, pu.escape_latex(v_description) + pl.NoEscape(r'\newline ') + pu.escape_latex(v_string_2)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_map(self, p_level):
        """
        Create a section with maps of all residences

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person = self.__person__

        #
        # TODO: Work in Progress
        #

        # Create path name for map
        # v_path = self.__document_path + r'Figures'

        # Create minipage
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('residences', self.__language__), p_label=False) as v_sub_level:
            # Create Tikz drawing with map as background
            # v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))

            # Create nodes
            v_scope_open = False
            v_done_list = []
            v_counter = 0

            for v_residence in v_person.get_events(gramps_db.c_residential_events_set):
                v_counter = v_counter + 1

                # Split date from place
                # v_date = v_residence.get_date()
                v_place = v_residence.get_place()

                # Find place name and coordinates
                v_name = v_place.__city_to_text__()
                v_latitude = v_place.__latitude__
                v_longitude = v_place.__longitude__

                # Debug
                logging.debug('v_name, v_longitude, v_latitude: %s, %5.3f. %5.3f', v_name, v_longitude, v_latitude)

                v_country = v_place.get_country()
                v_country_code = v_country.__place_code__
                if len(v_country_code) == 0:
                    v_country_code = v_country.__place_name__

                # 20220109: Limit number of maps to The Netherlands, Western Europe and the World
                if v_country_code != 'NLD':
                    v_region_list = support_functions.get_country_continent_subregion(v_country_code)
                    if v_region_list[1] == 'Western Europe':
                        v_country_code = 'WEU'
                    elif v_region_list[0] == 'Europe':
                        v_country_code = 'EUR'
                    else:
                        v_country_code = 'WLD'

                # Create path / file name for the map
                v_file_path = support_functions.create_map(self.__figures_path__, v_country_code)

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
                v_coordinates = support_functions.get_country_min_max_coordinates(v_country_code)
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

        # Create temporary list and sort
        v_event_list = []
        for v_event in v_person.get_events(gramps_db.c_residential_events_set):
            v_event_list.append(v_event)

        if len(v_event_list) > 0:
            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            # Create section with Residential Information
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with latex.create_sub_level(p_level=p_level, p_title=language.translate('residences', self.__language__), p_label=False) as v_sub_level:
                # Create nodes
                v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))
                v_sub_level.append(pu.NoEscape(r'\matrix[row sep=5mm, column sep=2mm]{'))

                v_counter = 0
                for v_event in v_event_list:
                    v_counter = v_counter + 1

                    v_string_1 = ''
                    v_date = v_event.get_date()
                    if v_date is not None:
                        v_string_1 = v_date.get_start_date_text()

                    v_string_2 = ''
                    v_place = v_event.get_place()
                    if v_place is not None:
                        v_string_2 = v_place.__street_to_text__()
                        if len(v_string_2) > 0:
                            v_string_2 = v_string_2 + ", " + v_place.__city_to_text__()
                        else:
                            v_string_2 = v_place.__city_to_text__()

                    v_string_3 = r'\node (p' + str(v_counter) + r') [date] {\small ' + v_string_1 + r'}; & '
                    v_string_3 = v_string_3 + r'\node [text width=10cm] {\small ' + pu.escape_latex(v_string_2) + r'};\\'
                    v_sub_level.append(pu.NoEscape(v_string_3))

                v_sub_level.append(pu.NoEscape(r'};'))

                # Create graph
                v_sub_level.append(pu.NoEscape(r'\graph [use existing nodes] {'))

                for v_count in range(2, v_counter + 1):
                    v_sub_level.append(pu.NoEscape(r'p' + str(v_count-1) + ' -> p' + str(v_count) + r';'))

                v_sub_level.append(pu.NoEscape(r'};'))
                v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_residence_section_table(self, p_level) -> None:
        """
        Create a section with a list of all residences in a table format

        @param p_level: level of the chapter / section
        @return: None
        """

        v_person: person.Person = self.__person__

        # Create temporary list and sort
        v_event_list: list[event.Event] = []
        for v_event in v_person.get_events(gramps_db.c_residential_events_set):
            v_event_list.append(v_event)

        if len(v_event_list) > 0:
            f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_start_date().year, x.get_date().get_start_date().month, x.get_date().get_start_date().day) if (x.get_date().get_start_date() is not None) else '-'
            v_event_list.sort(key=f_date_func)

            # Create section with Residential Information
            p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
            with latex.create_sub_level(p_level=p_level, p_title=language.translate('residences', self.__language__), p_label=False) as v_sub_level:
                with v_sub_level.create(pl.LongTabu(pl.NoEscape(r"p{\dimexpr.4\textwidth} p{\dimexpr.6\textwidth}"), row_height=1.5)) as v_table:
                    # Header row
                    v_table.add_row([pu.bold(language.translate('date', self.__language__)), pu.bold(language.translate('residence', self.__language__))])
                    v_table.add_hline()
                    v_table.end_table_header()

                    for v_event in v_event_list:
                        v_string_1 = ''
                        v_date = v_event.get_date()
                        if v_date is not None:
                            v_string_1 = v_date.__date_to_text__()

                        v_string_2 = ''
                        v_place = v_event.get_place()
                        if v_place is not None:
                            v_string_2 = v_place.__street_to_text__(True)
                            if len(v_string_2) > 0:
                                v_string_2 = v_string_2 + ", " + v_place.__city_to_text__()
                            else:
                                v_string_2 = v_place.__city_to_text__()

                        v_table.add_row([v_string_1, pu.escape_latex(v_string_2)])

                v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def __write_timeline_section(self, p_level):
        """
        Create section with timeline of life

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        def __date_to_serial(p_date: datetime.date = None) -> float:
            """
            Calculates for a given date the number of seconds since 1 january 1800

            @return: v_value: float
            """

            v_value: float = 0
            if p_date is not None:
                v_value = (datetime.datetime(p_date.year, p_date.month, p_date.day) - datetime.datetime(1800, 1, 1)) / datetime.timedelta(seconds=1)

            return v_value

        def __date_to_timeline(p_date: datetime.date, p_timeline_start_date: datetime.date, p_timeline_end_date: datetime.date, p_mean: float=None, p_std: float=None, p_length_timeline: int=20) -> float:
            """
            Calculates the y-coordinate on the timeline for a given date.
            This is either equidistant, or scaled according the cumulative distribution function of the normal distribution of all dates to be plotted.

            :param p_date: date for which y-coordinate is to be calculated
            :param p_timeline_start_date: first date on the timeline
            :param p_timeline_end_date: last date on the timeline
            :param p_mean: average value for the events on the timeline; in case a normal distribution was calculated
            :param p_std: standard deviation of the events on the timeline; in case a normal distribution was calculated
            :param p_length_timeline: length of the timeline, in cm.
            """

            if (p_date is not None) and (p_timeline_start_date is not None) and (p_timeline_end_date is not None):
                v_x_value = __date_to_serial(p_date)
                v_value_1 = __date_to_serial(p_timeline_start_date)
                v_value_2 = __date_to_serial(p_timeline_end_date)
                v_y_value = (v_x_value - v_value_1) * p_length_timeline / (v_value_2 - v_value_1)

                if (p_mean is not None) and (p_std is not None) and (p_std != 0):
                    # 'Cumulative distribution function for the standard normal distribution'
                    v_erf_x_value = (v_x_value - p_mean) / (p_std * math.sqrt(2.0))
                    v_cdf =  (1.0 + math.erf(v_erf_x_value)) / 2.0

                    if v_cdf > 0:
                        v_y_value = p_length_timeline * v_cdf  # + v_translate_mean
                    else:
                        logging.warning(f"Division by zero: v_cdf = {v_cdf}")

                if (v_y_value < 0) or (v_y_value > p_length_timeline):
                    logging.warning(f"Error in calculation: p_date, p_timeline_start_date, p_timeline_end_date, v_y_value = {p_date}, {p_timeline_start_date}, {p_timeline_end_date}, {v_y_value} for person {self.__person__.__gramps_id__}")
            else:
                v_y_value = 0
                logging.warning(f"Function parameters not given: p_date, p_timeline_start_date, p_timeline_end_date: {p_date}, {p_timeline_start_date}, {p_timeline_end_date}")

            return v_y_value

        def __calculate_start_end_dates(p_birth_date: date.Date, p_death_date: date.Date) -> tuple[datetime.date, datetime.date]:
            """

            :param p_birth_date:
            :param p_death_date:
            :return:
            """

            v_s_date: datetime.date # start date
            v_e_date: datetime.date # end date

            if (p_birth_date is None) or (p_birth_date.get_start_date() is None):
                if (p_death_date is None) or (p_death_date.get_start_date() is None):
                    v_s_date = datetime.date(datetime.date.today().year, 1, 1)
                else:
                    v_s_date = datetime.date(p_death_date.get_start_date().year - 100, 1, 1)
            else:
                v_s_date = datetime.date(p_birth_date.get_start_date().year, 1, 1)

            if (p_death_date is None) or (p_death_date.get_start_date() is None):
                v_e_date = datetime.date(v_s_date.year + 100, 1, 1)
            else:
                v_e_date = datetime.date(p_death_date.get_start_date().year + 1, 1, 1)

            v_today = datetime.date.today()
            if v_e_date > v_today:
                v_e_date = datetime.date(v_today.year + 1, 1, 1)

            # Round down / up to decennia
            v_s_date = datetime.date(int(support_functions.round_down(v_s_date.year, -1)), 1, 1)
            v_e_date = datetime.date(int(support_functions.round_up(v_e_date.year, -1)), 1, 1)

            return v_s_date, v_e_date

        #
        # Start __write_timeline_section
        #

        # Initialise variables
        v_person: person.Person = self.__person__

        v_birth_date: date.Date|None = None
        v_death_date: date.Date|None = None


        #
        # Collect all vital events in a list
        #

        v_timeline_events: list[event.Event] = []
        v_number_left_events: int = 0
        v_number_right_events: int = 0

        v_generator = v_person.get_events(gramps_db.c_vital_events_set.union(gramps_db.c_residential_events_set), {gramps_db.c_role_primary, gramps_db.c_role_family})
        for v_event in v_generator:
            # Add event to list
            if v_event.get_date() is not None:
                if v_event.get_date().get_start_date() is not None:
                    v_timeline_events.append(v_event)

                    if v_event.get_type().get_value() in gramps_db.c_vital_events_set:
                        v_number_left_events = v_number_left_events + 1

                    elif v_event.get_type().get_value() in gramps_db.c_residential_events_set:
                        v_number_right_events = v_number_right_events + 1

            # Store birth / baptism and death / burial separately for later comparison
            v_type: int = v_event.get_type().get_value()
            v_date: date.Date = v_event.get_date()

            if v_type == gramps_db.c_event_birth:
                v_birth_date = v_date
            elif (v_type == gramps_db.c_event_baptism) and (v_birth_date is None):
                v_birth_date = v_date
            elif v_type == gramps_db.c_event_death:
                v_death_date = v_date
            elif (v_type == gramps_db.c_event_burial) and (v_death_date is None):
                v_death_date = v_date

        # Merge the family events
        for v_family_handle in v_person.__family_list__:
            v_family = family.Family(v_family_handle, self.__cursor__)

            for v_event in v_family.get_events(gramps_db.c_family_events_set.union(gramps_db.c_residential_events_set)):
                if v_event.get_date() is not None:
                    if v_event.get_date().get_start_date() is not None:
                        v_timeline_events.append(v_event)

                        if v_event.get_type().get_value() in gramps_db.c_family_events_set:
                            v_number_left_events = v_number_left_events + 1

                        elif v_event.get_type().get_value() in gramps_db.c_residential_events_set:
                            v_number_right_events = v_number_right_events + 1

        # Merge the vital information of partners
        for v_partner_handle in v_person.get_partner_handles():
            if v_partner_handle is not None:  # TODO: Also handle families with unknown partners
                v_partner = person.Person(v_partner_handle, self.__cursor__)

                for v_event in v_partner.get_events({gramps_db.c_event_birth, gramps_db.c_event_death}):
                    if v_event.get_date() is not None:
                        v_start_date = v_event.get_date().get_start_date()

                        if v_start_date is not None:
                            if v_death_date is not None:
                                if v_start_date < v_death_date.get_start_date():
                                    v_timeline_events.append(v_event)
                                    v_number_left_events = v_number_left_events + 1
                            else:
                                v_timeline_events.append(v_event)
                                v_number_left_events = v_number_left_events + 1

        # Merge the vital information of children
        for v_child_handle in v_person.get_child_handles():
            if v_child_handle is not None:
                v_child = person.Person(v_child_handle, self.__cursor__)

                for v_event in v_child.get_events({gramps_db.c_event_birth, gramps_db.c_event_baptism, gramps_db.c_event_death, gramps_db.c_event_burial}):
                    if v_event.get_date() is not None:
                        v_start_date = v_event.get_date().get_start_date()

                        if v_start_date is not None:
                            if v_death_date is not None:
                                if v_start_date < v_death_date.get_start_date():
                                    v_timeline_events.append(v_event)
                                    v_number_left_events = v_number_left_events + 1
                            else:
                                v_timeline_events.append(v_event)
                                v_number_left_events = v_number_left_events + 1

        # Adjust number of events left / right
        if v_number_left_events > 1:
            v_number_left_events = v_number_left_events - 1

        if v_number_right_events > 1:
            v_number_right_events = v_number_right_events - 1

        # Sort the timeline event list
        f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x.get_date().get_mid_date().year, x.get_date().get_mid_date().month, x.get_date().get_mid_date().day) if (x.get_date().get_mid_date() is not None) else '-'
        v_timeline_events.sort(key=f_date_func)

        # Calculate mean and standard deviation based on start year; this improves visibility on the timeline for decades where more events are happening; see __calculate_start_end_dates
        v_values = [__date_to_serial(x.get_date().get_mid_date()) for x in v_timeline_events]
        v_mean = None
        v_std = None
        if len(v_values) > 0:
            v_mean = numpy.mean(v_values)
            v_std = numpy.std(v_values)
            if v_std == 0:
                v_std = None

        # Determine the start and end dates for the timeline
        v_start_date, v_end_date = __calculate_start_end_dates(v_birth_date, v_death_date)

        #
        # Create the timeline section
        #
        p_level.append(pl.NoEscape(r"\needspace{\minspace}"))
        with latex.create_sub_level(p_level=p_level, p_title=language.translate('Timeline', self.__language__), p_label=False) as v_sub_level:
            v_sub_level.append(pu.NoEscape(r'\makebox[\textwidth]{\makebox[0.8\paperwidth]{'))
            # Create nodes
            v_sub_level.append(pu.NoEscape(r'\begin{tikzpicture}'))

            # Define style
            v_sub_level.append(pu.NoEscape(r'[eventmarker/.style = {circle, draw = red!50, fill = red!20, thick, inner sep = 0 pt, minimum size = 5 pt},'))
            v_sub_level.append(pu.NoEscape(r'eventlabel/.style = {},'))
            v_sub_level.append(pu.NoEscape(r'residencemarker/.style = {circle, draw = blue!50, fill = blue!20, thick, inner sep = 0 pt, minimum size = 5 pt},'))
            v_sub_level.append(pu.NoEscape(r'residenceperiod/.style = {rounded corners, draw = blue!50, fill = blue!20, thick, inner sep = 0 pt, minimum size = 5 pt},'))
            v_sub_level.append(pu.NoEscape(r'residencelink/.style = {draw = blue!50},'))
            v_sub_level.append(pu.NoEscape(r'residencelabel/.style = {},'))
            v_sub_level.append(pu.NoEscape(r'nostyle/.style = {}]'))

            # Calculate the start and end points of the timeline
            v_start_point: float = __date_to_timeline(v_start_date, v_start_date, v_end_date, v_mean, v_std)
            v_end_point: float = __date_to_timeline(v_end_date, v_start_date, v_end_date, v_mean, v_std)

            # Draw the events in the timeline
            v_count = 0
            v_count_left = 0
            v_count_right = 0
            c_text_width = 7.5

            # First all Residences...
            for v_event in v_timeline_events:
                v_date: date.Date = v_event.get_date()
                v_type: int = v_event.get_type().get_value()
                v_place: place.Place = v_event.get_place()
                v_description: str = v_event.get_description()

                # The event should have a date and a place
                if (v_date is not None) and (v_place is not None):
                    v_place_text = v_place.__street_to_text__()
                    if len(v_place_text) > 0:
                        v_place_text = v_place_text + ", " + v_place.__city_to_text__()
                    else:
                        v_place_text = v_place.__city_to_text__()

                    if v_type in gramps_db.c_residential_events_set:
                        # Residence to the right
                        if (v_date.get_start_date() is not None) and (v_date.get_end_date() is None):  # Single date events
                            v_date_1: datetime.date = v_event.get_date().get_start_date()
                            v_date_point_1: float = __date_to_timeline(v_date_1, v_start_date, v_end_date, v_mean, v_std)

                            v_label_point_1: float = v_start_point + v_count_right * (v_end_point - v_start_point) / v_number_right_events
                            v_count_right = v_count_right + 1

                            v_count = v_count + 1
                            v_marker_name_1: str = r'marker_' + str(v_count)
                            v_label_name_1: str = r'label_' + str(v_count)

                            if len(v_description) > 0:
                                v_label: str = v_description + r'\\' + v_date.__date_to_text__()
                            else:
                                v_label: str = v_place_text + r'\\' + v_date.__date_to_text__()

                            v_sub_level.append(pu.NoEscape(r'\node [residencemarker] (' + v_marker_name_1 + r') at (0 cm,' + str(v_date_point_1) + r' cm) {};'))
                            # v_sub_level.append(pu.NoEscape(r'\node [residencelabel, right=of ' + v_marker_name_1 + r', align=left, text width=' + str(c_text_width) + r' cm] (' + v_label_name_1 + r') at (+1.0 cm,' + str(v_date_point_1) + r' cm) {\small ' + v_label + r'};'))
                            v_sub_level.append(pu.NoEscape(r'\node [residencelabel, right=of ' + v_marker_name_1 + r', align=left, text width=' + str(c_text_width) + r' cm] (' + v_label_name_1 + r') at (+1.0 cm,' + str(v_label_point_1) + r' cm) {\small ' + v_label + r'};'))
                            v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_1 + r'.east) -- (' + v_label_name_1 + r'.west);'))
                            v_sub_level.append(pu.NoEscape(r'%'))

                        elif (v_date.get_start_date() is not None) and (v_date.get_end_date() is not None):  # Dual date events
                            v_date_1: datetime.date = v_date.get_start_date()
                            v_date_2: datetime.date = v_date.get_end_date()

                            v_date_point_1: float = __date_to_timeline(v_date_1, v_start_date, v_end_date, v_mean, v_std)
                            v_date_point_2: float = __date_to_timeline(v_date_2, v_start_date, v_end_date, v_mean, v_std)
                            v_date_point_3: float = (v_date_point_1 + v_date_point_2) / 2

                            v_label_point_1: float = v_start_point + v_count_right * (v_end_point - v_start_point) / v_number_right_events
                            v_count_right = v_count_right + 1

                            v_hor_point: float = 0.0  # 1.0 if v_count_right % 2 == 0 else 2.0 # TODO: Remove?

                            v_count = v_count + 1
                            v_marker_name_1: str = r'marker_' + str(v_count)

                            v_count = v_count + 1
                            v_marker_name_2: str = r'marker_' + str(v_count)

                            v_count = v_count + 1
                            v_marker_name_3: str = r'marker_' + str(v_count)

                            v_count = v_count + 1
                            v_label_name: str = r'label_' + str(v_count)

                            if len(v_description) > 0:
                                v_label: str = v_description + r'\\' + v_date.__date_to_text__()
                            else:
                                v_label: str = v_place_text + r'\\' + v_date.__date_to_text__()

                            # Coordinates for time span
                            v_sub_level.append(pu.NoEscape(r'\coordinate (' + v_marker_name_1 + r') at (' + str(v_hor_point) + 'cm - 0.1cm,' + str(v_date_point_1) + r' cm) {};'))
                            v_sub_level.append(pu.NoEscape(r'\coordinate (' + v_marker_name_2 + r') at (' + str(v_hor_point) + 'cm + 0.1cm,' + str(v_date_point_2) + r' cm) {};'))
                            v_sub_level.append(pu.NoEscape(r'\coordinate (' + v_marker_name_3 + r') at (' + str(v_hor_point) + 'cm + 0.1cm,' + str(v_date_point_3) + r' cm) {};'))

                            v_sub_level.append(pu.NoEscape(r'\draw [residenceperiod] (' + v_marker_name_1 + r') rectangle (' + v_marker_name_2 + r');'))
                            # v_sub_level.append(pu.NoEscape(r'\node [residencelabel, right=of ' + v_marker_name_3 + r'align=left, text width=' + str(c_text_width) + r' cm] (' + v_label_name + r') at (+1.0 cm,' + str(v_date_point_3) + r' cm) {\small ' + v_label + r'};'))
                            # v_sub_level.append(pu.NoEscape(r'\node [residencelabel, right=of ' + v_marker_name_3 + r'align=left, text width=' + str(c_text_width) + r' cm, anchor=west] (' + v_label_name + r') at (+1.0 cm,' + str(v_date_point_3) + r' cm) {\small ' + v_label + r'};'))
                            v_sub_level.append(pu.NoEscape(r'\node [residencelabel, right=of ' + v_marker_name_3 + r'align=left, text width=' + str(c_text_width) + r' cm, anchor=west] (' + v_label_name + r') at (+1.0 cm,' + str(v_label_point_1) + r' cm) {\small ' + v_label + r'};'))
                            v_sub_level.append(pu.NoEscape(r'\draw [residencelink] (' + v_marker_name_3 + r') -- (' + v_label_name + r'.west);'))

                            v_sub_level.append(pu.NoEscape(r'%'))

            # ...next all Life Events...
            for v_event in v_timeline_events:
                v_date: date.Date = v_event.get_date()
                v_type: int = v_event.get_type().get_value()
                # v_place = v_event.get_place().__street_to_text__()
                v_description: str = v_event.get_description()

                # The event should have a date and a description
                if (v_date is not None) and (len(v_description) > 0):
                    if v_type in gramps_db.c_vital_events_set.union(gramps_db.c_family_events_set):
                        # Life events to the left
                        v_date_1: datetime.date = v_date.get_start_date()
                        v_date_point_1: float = __date_to_timeline(v_date_1, v_start_date, v_end_date, v_mean, v_std)
                        v_label_point_1: float = v_start_point + v_count_left * (v_end_point - v_start_point) / v_number_left_events

                        v_count_left = v_count_left + 1

                        v_count = v_count + 1
                        v_marker_name_1: str = r'marker_' + str(v_count)
                        v_label_name_1: str = r'label_' + str(v_count)
                        v_label: str = pu.escape_latex(v_description)

                        v_sub_level.append(pu.NoEscape(r'\node [eventmarker] (' + v_marker_name_1 + r') at (0 cm,' + str(v_date_point_1) + r' cm) {};'))
                        v_sub_level.append(pu.NoEscape(r'\node [eventlabel, left=of ' + v_marker_name_1 + r', align=right, text width=' + str(c_text_width) + r' cm] (' + v_label_name_1 + r') at (-1.0 cm,' + str(v_label_point_1) + r' cm) {\small ' + v_label + r'};'))
                        v_sub_level.append(pu.NoEscape(r'\draw (' + v_marker_name_1 + r'.west) -- (' + v_label_name_1 + r'.east);'))
                        v_sub_level.append(pu.NoEscape(r'%'))

            # ...then the major timeline...
            v_sub_level.append(pu.NoEscape(r'\draw[->, very thick] (0cm, ' + str(v_start_point) + r'cm) -- (0cm, ' + str(v_end_point) + r'cm);'))
            v_sub_level.append(pu.NoEscape(r'%'))

            # ... and finally the decennial tick lines and the year labels
            v_string: str = str(v_start_point) + r'/' + str(v_start_date.year)
            for v_year in range(v_start_date.year + 10, v_end_date.year, 10):
                v_date: datetime.date = datetime.date(v_year, 1, 1)
                v_date_point = __date_to_timeline(v_date, v_start_date, v_end_date, v_mean, v_std)
                v_string = v_string + r',' + str(v_date_point) + r'/' + str(v_year)

            v_sub_level.append(pu.NoEscape(r'\foreach \y/\ytext in {' + v_string + r'}'))
            v_sub_level.append(pu.NoEscape(r'\draw[thick, yshift =\y cm] (-2pt, 0pt) - - (2pt, 0pt) node[left=2pt, fill=white] {$\ytext$};'))
            v_sub_level.append(pu.NoEscape(r'%'))

            v_sub_level.append(pu.NoEscape(r'\end{tikzpicture}'))
            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

            v_sub_level.append(pu.NoEscape(r'}}'))

    def __write_photo_section(self, p_level) -> None:
        """
        Create section with photos

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        v_filtered_list: list[media_ref.MediaRef] = self.__get_filtered_photo_list()
        if len(v_filtered_list) > 0:
            self.__write_media_section(p_level, v_filtered_list, p_title="photos")

    def __write_document_section(self, p_level):
        """
        Create section with document scans

        @param p_level: the level of the section (chapter / section / subsection / etc.)
        @return: None
        """

        v_filtered_list: list[media_ref.MediaRef] = self.__get_filtered_document_list()
        if len(v_filtered_list) > 0:
            self.__write_media_section(p_level, v_filtered_list, p_title='documents')

    def __write_media_section(self, p_level, p_filtered_list: list[media_ref.MediaRef], p_title: str='media') -> None:
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
        with latex.create_sub_level(p_level=p_level, p_title=language.translate(p_title, self.__language__), p_label=False) as v_sub_level:
            #
            # 1. All media with notes
            #
            v_position = 'o'
            v_temp_list: list[media_ref.MediaRef] = p_filtered_list.copy()  # Use temporary list, so items can be removed while iterating
            for v_media_ref in v_temp_list:
                v_media = v_media_ref.get_media()
                v_media_rect = v_media_ref.get_rect()

                v_media_path = v_media.__media_path__
                v_media_title = v_media.__description__
                v_media_notes = self.__get_filtered_note_list(v_media.__note_list__)

                # TODO: dit gaat mis als het een note met tag 'source' betreft
                if len(v_media_notes) > 0:
                    # Media contains notes
                    v_position = 'o' if v_position == 'i' else 'i'  # Alternate position of image / text
                    self.__document_with_note(v_sub_level, v_media_path, v_media_title, v_media_notes, v_media_rect, v_position)  # 20220322: Added v_media_rect

                    # Done, remove from list
                    p_filtered_list.remove(v_media_ref)

            #
            # 2. Remaining media, side by side
            #
            v_counter = 0

            v_temp_list = p_filtered_list.copy()  # Use temporary list, so items can be removed while iterating
            for v_media_ref in v_temp_list:
                v_media = v_media_ref.get_media()
                v_media_rect = v_media_ref.get_rect()

                v_counter = v_counter + 1
                if v_counter % 2 == 1:
                    v_media_path_1 = v_media.__media_path__
                    v_media_title_1 = v_media.__description__
                    v_media_rect_1 = v_media_rect

                    # Remove media_1 from list
                    p_filtered_list.remove(v_media_ref)
                else:
                    v_media_path_2 = v_media.__media_path__
                    v_media_title_2 = v_media.__description__
                    v_media_rect_2 = v_media_rect

                    support_functions.picture_side_by_side_equal_height(v_sub_level, v_media_path_1, v_media_path_2, v_media_title_1, v_media_title_2, v_media_rect_1, v_media_rect_2)

                    # Remove media_2 from list
                    p_filtered_list.remove(v_media_ref)

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
                v_sub_level.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

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

                    # with v_sub_level.create(latex.Figure(position='htpb')) as vPhoto:
                    #     vPhoto.add_image(pl.NoEscape(v_media_path_1))
                    #     vPhoto.add_caption(pu.escape_latex(v_media_title_1))

                # 20230313: End the minipage
                v_sub_level.append(pl.NoEscape(r'\end{minipage}'))

            v_sub_level.append(pl.NoEscape(r'\FloatBarrier'))

    def get_person(self) -> person.Person:
        return self.__person__

    def write_person_chapter(self) -> None:
        """
        Writes the person to a separate chapter in a subdocument

        @param: None
        @return: None
        """

        v_person: person.Person = self.get_person()

        # Display progress
        logging.info(f"Writing a chapter about: {v_person.__given_names__} {v_person.__surname__}")

        # Create a new chapter for the active person
        v_chapter = latex.Chapter(title=v_person.__given_names__ + ' ' + v_person.__surname__, label=v_person.__gramps_id__)

        self.__write_life_sketch_section(v_chapter)
        self.__write_vital_information_section(v_chapter)
        # self.__WriteFamilySection(v_chapter)
        self.__write_parental_section_graph(v_chapter)
        # self.__write_parental_section_table(v_chapter)
        self.__write_partner_sections_graph(v_chapter)
        # self.__write_partner_sections_table(v_chapter)
        self.__write_education_section(v_chapter)
        self.__write_profession_section(v_chapter)
        self.__write_residence_section_timeline(v_chapter)
        # self.__write_residence_section_table(v_chapter)
        # self.__WriteResidenceSection_Map(v_chapter)
        self.__write_photo_section(v_chapter)
        self.__write_document_section(v_chapter)
        self.__write_timeline_section(v_chapter)

        v_chapter.generate_tex(filepath=self.__chapter_path__ + v_person.__gramps_id__)
