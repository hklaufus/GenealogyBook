import json
import logging

import date
import event
import event_ref
import family
import media_ref
import note
import person_ref
import place
import tag

import gramps_db
import language


class Person:
    __handle__: str = None
    __gramps_id__: str = None
    __gender__: int = None
    __call_name__: str = None
    __given_names__: str = None
    __surname__: str = None
    __alternate_names__: list[str] = None
    __death_ref_index__: int = None
    __birth_ref_index__: int = None
    __event_ref_list__: list[event_ref.EventRef] = None
    __family_list__: list[str] = None
    __parent_family_list__: list[str] = None
    __media_list__: list[media_ref.MediaRef] = None
    __address_list__: list[str] = None
    __attribute_list__: list[str] = None
    __urls__: list[str] = None
    # __lds_ord_base__: list[str] = None
    __citation_list__: list[str] = None
    __note_list__: list[note.Note] = None
    __change__: int = None
    __tag_list__: list[tag.Tag] = None
    __private__: bool = None
    __person_ref_list__: list[person_ref.PersonRef] = None

    def __init__(self, p_person_handle, p_cursor):
        self.__cursor__ = p_cursor
        self.__cursor__.execute('SELECT json_data FROM person WHERE handle=?', [p_person_handle])
        v_record = self.__cursor__.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]
            if v_json_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#1._Person
                v_decoder = json.JSONDecoder()
                v_person_data = v_decoder.decode(v_json_data)

                self.__handle__ = v_person_data['handle']
                self.__gramps_id__ = v_person_data['gramps_id']
                self.__gender__ = v_person_data['gender']

                v_primary_name = v_person_data['primary_name']
                self.__call_name__ = v_primary_name['call'].strip()
                self.__given_names__ = v_primary_name['first_name'].strip()

                v_surname_list = v_primary_name['surname_list']
                v_surname = v_surname_list[0]
                self.__surname__ = v_surname['surname'].strip()

                self.__alternate_names__ = v_person_data['alternate_names']
                self.__death_ref_index__ = v_person_data['death_ref_index']
                self.__birth_ref_index__ = v_person_data['birth_ref_index']
                self.__event_ref_list__ = [event_ref.EventRef(p_event_ref=v_event_ref, p_cursor=p_cursor) for v_event_ref in v_person_data['event_ref_list']]
                self.__family_list__ = v_person_data['family_list']
                self.__parent_family_list__ = v_person_data['parent_family_list']
                self.__media_list__ = [media_ref.MediaRef(p_media_ref=v_media_ref, p_cursor=p_cursor) for v_media_ref in v_person_data['media_list']]
                self.__address_list__ = v_person_data['address_list']
                self.__attribute_list__ = v_person_data['attribute_list']
                self.__urls__ = v_person_data['urls']
                # self.__lds_ord_base__ = v_person_data[14]
                self.__citation_list__ = v_person_data['citation_list']
                self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in v_person_data['note_list']]
                self.__change__ = v_person_data['change']
                self.__tag_list__ = [tag.Tag(p_tag_handle=v_tag, p_cursor=p_cursor) for v_tag in v_person_data['tag_list']]
                self.__private__ = v_person_data['private']
                self.__person_ref_list__ = [person_ref.PersonRef(p_person_ref=v_person_ref, p_cursor=p_cursor) for v_person_ref in v_person_data['person_ref_list']]

        # TODO: This is a tag list NOT related to one person; this does not belong here
        self.__tag_dictionary__ = gramps_db.get_tag_dictionary(self.__cursor__)

    def get_gramps_id(self):
        """
        Returns the Gramps ID of self
        """

        return self.__gramps_id__

    def get_source_status(self):
        """
        Checks whether scans are available for the events birth, marriage and death

        @return: v_source_status
        """

        v_source_status = {'b': '', 'm': '', 'd': ''}  # birth, marriage, death

        # Birth / baptism
        v_media_list = []
        for v_event in self.get_events(gramps_db.c_event_birth):  # Birth
            v_media_list.extend(v_event.__media_list__)

        for v_event in self.get_events(gramps_db.c_event_baptism):  # Baptism
            v_media_list.extend(v_event.__media_list__)

        if len(v_media_list) > 0:
            v_source_status['b'] = 'b'

        # Marriage
        for v_family_handle in self.__family_list__:
            v_family = family.Family(v_family_handle, self.__cursor__)

            for v_event in v_family.get_events():
                v_type = v_event.get_type()
                v_media_list = v_event.__media_list__

                # 1 = Marriage, 2 = Marriage Settlement, 3 = Marriage License, 4 = Marriage Contract
                if ((v_type == gramps_db.c_event_marriage) or (v_type == gramps_db.c_event_marriage_settlement) or (v_type == gramps_db.c_event_marriage_license) or (v_type == gramps_db.c_event_marriage_contract)) and (len(v_media_list) > 0):
                    v_source_status['m'] = 'm'

        # Death / Burial
        v_media_list = []
        for v_event in self.get_events(gramps_db.c_event_death):  # Death
            v_media_list.extend(v_event.__media_list__)

        for v_event in self.get_events(gramps_db.c_event_burial):  # Burial
            v_media_list.extend(v_event.__media_list__)

        if len(v_media_list) > 0:
            v_source_status['d'] = 'd'

        return v_source_status

    def get_birth_date(self):
        """
        Returns the birthdate in datetime.date format

        @return: v_birth_date: datetime.date
        """

        v_date = None

        if self.__birth_ref_index__ >= 0:
            v_event_ref = self.__event_ref_list__[self.__birth_ref_index__]
            v_event = v_event_ref.get_event()
            v_date = v_event.get_date().get_start_date()

        return v_date

    def get_death_date(self):
        """
        Returns the death date in datetime.date format

        @return: v_birth_date: datetime.date
        """

        v_date = None

        if self.__death_ref_index__ >= 0:
            v_event_ref = self.__event_ref_list__[self.__death_ref_index__]
            v_event = event_ref.EventRef(v_event_ref, self.__cursor__).get_event()
            v_date = v_event.get_date().get_start_date()

        return v_date

    def get_father_handle(self):
        """
        Returns the handles of the father(s) of the current person

        @return: v_father_handles [str]
        """

        v_father_handle = None

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs, only returning first father..")

        if len(self.__parent_family_list__) > 0:
            v_family_handle = self.__parent_family_list__[0]
            v_family = family.Family(v_family_handle, self.__cursor__)
            v_father_handle = v_family.get_father_handle()

        return v_father_handle

    def get_father(self):
        return Person(p_person_handle=self.get_father_handle(), p_cursor=self.__cursor__)

    def get_mother_handle(self):
        """
        Returns the handles of the mother(s) of the current person

        @return: v_mother_handles [str]
        """

        v_mother_handle = None

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs, only returning first mother..")

        if len(self.__parent_family_list__) > 0:
            v_family_handle = self.__parent_family_list__[0]
            v_family = family.Family(v_family_handle, self.__cursor__)
            v_mother_handle = v_family.get_mother_handle()

        return v_mother_handle

    def get_mother(self):
        return Person(p_person_handle=self.get_mother_handle(), p_cursor=self.__cursor__)

    def get_sibling_handles(self):
        """
        Returns the handles of the sibling(s) of the current person

        @return: v_sibling_handles [str]
        """

        v_sibling_handles: list[str] = []

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs..")

        for v_family_handle in self.__parent_family_list__:
            v_family = family.Family(v_family_handle, self.__cursor__)
            v_child_handle_list = v_family.get_child_handle_list()
            v_child_handle_list.remove(self.__handle__)
            v_sibling_handles = v_sibling_handles + v_child_handle_list

        return v_sibling_handles

    def get_partner_handles(self) -> list[str]:
        """
        Returns the handles of the partner(s) of the current person

        @return: v_partner_handles
        """

        v_partner_handles: list[str] = []

        for v_family_handle in self.__family_list__:
            v_family = family.Family(v_family_handle, self.__cursor__)
            v_father_handle: str = v_family.get_father_handle()
            v_mother_handle: str = v_family.get_mother_handle()

            if v_father_handle == self.__handle__:
                v_partner_handles.append(v_mother_handle)
            else:
                v_partner_handles.append(v_father_handle)

        return v_partner_handles

    def get_child_handles(self) -> list[str]:
        """
        Returns the GrampsDB handles for all children

        @return: v_child_handles: [str]
        """

        v_child_handles: list[str] = []

        for v_family_handle in self.__family_list__:
            v_family = family.Family(v_family_handle, self.__cursor__)
            v_child_handles = v_child_handles + v_family.get_child_handle_list()

        return v_child_handles

    def get_events(self, p_type: int|set[int]=None, p_role: int|set[int]=None):
        """
        Creates a generator list object

        @param: p_type: set of types to filter on
        @param: p_role: set of roles to filter on

        @return: v_event
        """

        # Convert parameters to set
        v_use_type: set[int]
        if (p_type is not None) and isinstance(p_type, int):
            v_use_type = {p_type}
        else:
            v_use_type = p_type

        v_use_role: set[int]
        if (p_role is not None) and isinstance(p_role, int):
            v_use_role = {p_role}
        else:
            v_use_role = p_role

        for v_event_ref in self.__event_ref_list__:
            if (p_role is None) or (v_event_ref.get_role().get_value() in v_use_role):
                v_event: event.Event = v_event_ref.get_event()

                if len(v_event.__description__) == 0:
                    v_type_string: str = gramps_db.c_event_type_dict[v_event.get_type().get_value()]
                    v_name_string: str = self.__given_names__ + ' ' + self.__surname__

                    v_date_place_string: str = '['

                    v_place: place.Place = v_event.get_place()
                    if v_place is not None:
                        v_place_string: str = v_place.__place_to_text__()
                        if len(v_place_string) > 0:
                            v_date_place_string = v_date_place_string + v_place_string + ', '

                    v_date: date.Date = v_event.get_date()
                    if v_date is not None:
                        v_date_string: str = v_date.__date_to_text__()
                        if len(v_date_string) > 0:
                            v_date_place_string = v_date_place_string + v_date_string

                    v_date_place_string = v_date_place_string + ']'

                    v_event.__description__ = language.translate(v_type_string) + ' ' + v_name_string + ' ' + v_date_place_string

                if (p_type is None) or (v_event.get_type().get_value() in v_use_type):
                    yield v_event

    def ___log__(self):
        """
        Print the contents of the person for debugging purposes.

        @return: None
        """

        print("*** Start Person Log ***")
        print("__handle__: {}".format(self.__handle__))
        print("__gramps_id__: {}".format(self.__gramps_id__))
        print("__gender__: {}".format(self.__gender__))
        print("__call_name__: {}".format(self.__call_name__))
        print("__given_names__: {}".format(self.__given_names__))
        print("__surname__: {}".format(self.__surname__))
        print("__alternate_name__: {}".format(self.__alternate_names__))
        print("__death_ref_index__: {}".format(self.__death_ref_index__))
        print("__birth_ref_index__: {}".format(self.__birth_ref_index__))
        print("__event_ref_list__: {}".format(self.__event_ref_list__))
        print("__family_list__: {}".format(self.__family_list__))
        print("__parent_family_list__: {}".format(self.__family_list__))
        print("__media_base__: {}".format(self.__media_list__))
        print("__address_base__: {}".format(self.__address_list__))
        print("__attribute_base__: {}".format(self.__attribute_list__))
        print("__url_base__: {}".format(self.__urls__))
        # print("__lds_ord_base__: {}".format(self.__lds_ord_base__))
        print("__citation_base__: {}".format(self.__citation_list__))
        print("__note_base__: {}".format(self.__note_list__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_list__))
        print("__private__: {}".format(self.__private__))
        print("__person_ref_list__: {}".format(self.__person_ref_list__))
        print("*** End Person Log ***")
