import datetime
import logging
import pickle

import hkEvent
import hkEventRef
import hkFamily
import hkGrampsDb
import hkMedia
import hkNote
import hkTag


class Person:
    __handle__: str = None
    __gramps_id__: str = None
    __gender__: int = None
    __call_name__: str = None
    __given_names__: str = None
    __surname__: str = None
    __alternate_name__: [str] = None
    __death_ref_index__: int = None
    __birth_ref_index__: int = None
    __event_ref_list__: [hkEventRef.EventRef] = None
    __family_list__: [str] = None
    __parent_family_list__: [str] = None
    __media_base__: [hkMedia.Media] = None
    __address_base__: [str] = None
    __attribute_base__: [str] = None
    __url_base__: [str] = None
    # __lds_ord_base__: [str] = None
    __citation_base__: [str] = None
    __note_base__: [hkNote.Note] = None
    __change__: int = None
    __tag_base__: [hkTag.Tag] = None
    __private__: bool = None
    __person_ref_list__: [str] = None  # TODO: Check

    __person_event_dict__: dict[int, list[hkEvent.Event]]

    def __init__(self, p_person_handle, p_cursor):
        self.__cursor__ = p_cursor

        self.__cursor__.execute('SELECT given_name, surname, blob_data FROM person WHERE handle=?', [p_person_handle])
        v_record = self.__cursor__.fetchone()

        if v_record is not None:
            # self.__given_name = v_record[0]
            # self.__surname = v_record[1]

            v_blob_data = v_record[2]
            if v_blob_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#1._Person
                v_person_data = pickle.loads(v_blob_data)
                v_person_data = list(v_person_data)

                self.__handle__ = v_person_data[0]
                self.__gramps_id__ = v_person_data[1]
                self.__gender__ = v_person_data[2]

                v_primary_name = v_person_data[3]
                self.__call_name__ = v_primary_name[12].strip()
                self.__given_names__ = v_primary_name[4].strip()
                self.__surname__ = (v_primary_name[5][0][1].strip() + ' ' + v_primary_name[5][0][0].strip()).strip()

                self.__alternate_name__ = v_person_data[4]
                self.__death_ref_index__ = v_person_data[5]
                self.__birth_ref_index__ = v_person_data[6]
                self.__event_ref_list__ = v_person_data[7]
                self.__family_list__ = v_person_data[8]
                self.__parent_family_list__ = v_person_data[9]
                self.__media_base__ = v_person_data[10]
                self.__address_base__ = v_person_data[11]
                self.__attribute_base__ = v_person_data[12]
                self.__url_base__ = v_person_data[13]
                # self.__lds_ord_base__ = v_person_data[14]
                self.__citation_base__ = v_person_data[15]
                self.__note_base__ = v_person_data[16]
                self.__change__ = v_person_data[17]
                self.__tag_base__ = v_person_data[18]
                self.__private__ = v_person_data[19]
                self.__person_ref_list__ = v_person_data[20]

        self.__person_event_dict__ = self.__create_person_event_dict()
        self.__family_event_dict__ = self.__create_family_event_dict()

        self.__source_status__ = self.__get_source_status()

        # TODO: This is a tag list NOT related to one person; this does not belong here
        self.__tag_dictionary__ = hkGrampsDb.get_tag_dictionary(self.__cursor__)

    def __create_person_event_dict(self):
        """
        Creates a dictionary of personal events
        The key refers to the type of event (e.g. Profession); the value contains a list of events belonging to this event type (e.g. multiple professions within key Profession)
        Key:[event info, event info 2, event info 3]
        """

        v_person_event_dict = {}
        for v_event_ref in self.__event_ref_list__:
            v_event_handle = v_event_ref[3]
            v_event = hkEvent.Event(v_event_handle, self.__cursor__)

            # Filter on role
            v_role_type = v_event_ref[4][0]
            if (v_role_type == hkGrampsDb.c_role_primary) or (v_role_type == hkGrampsDb.c_role_family):
                # Check whether event type already exists as key...
                if v_event.get_type() in v_person_event_dict:
                    # ...if so, append event info to the dictionary entry
                    v_person_event_dict[v_event.get_type()].append(v_event)
                else:
                    # ...otherwise create a new entry
                    v_person_event_dict[v_event.get_type()] = [v_event]

                # Add event media to personal media list
                # self.__event_media_list__ = self.__event_media_list__ + v_event.__media_base__
                self.__media_base__ = self.__media_base__ + v_event.__media_base__

        return v_person_event_dict

    def __create_family_event_dict(self):
        v_family_event_dict = {}
        for v_family_handle in self.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_family_events = v_family.__event_ref_list__
            self.__media_base__ = self.__media_base__ + v_family.__media_base__  # Add family media to personal media list

            for v_family_event_ref in v_family_events:
                v_event_ref = hkEventRef.EventRef(v_family_event_ref, self.__cursor__)
                v_event = v_event_ref.get_event()

                # Filter on role
                v_role_type = v_event_ref.__role__  # v_event_ref[4][0]
                if (v_role_type == hkGrampsDb.c_role_primary) or (v_role_type == hkGrampsDb.c_role_family):
                    # Check whether event type already exists as key...
                    if v_event.get_type() in v_family_event_dict:
                        # ...if so, append event info to the dictionary entry
                        v_family_event_dict[v_event.get_type()].append(v_event)
                    else:
                        # ...otherwise create a new entry
                        v_family_event_dict[v_event.get_type()] = [v_event]

        return v_family_event_dict

    def __get_source_status(self):
        """ Checks whether scans are available for the events birth, marriage and death """
        v_source_status = {'b': '', 'm': '', 'd': ''}  # birth, marriage, death

        # Birth / baptism
        v_media_list = []
        if hkGrampsDb.c_event_birth in self.__person_event_dict__:  # Birth
            v_event_list = self.__person_event_dict__[hkGrampsDb.c_event_birth]
            v_event = v_event_list[0]
            v_media_list.extend(v_event.__media_base__)

        if hkGrampsDb.c_event_baptism in self.__person_event_dict__:  # Baptism
            v_event_list = self.__person_event_dict__[hkGrampsDb.c_event_baptism]
            v_event = v_event_list[0]
            v_media_list.extend(v_event.__media_base__)

        if len(v_media_list) > 0:
            v_source_status['b'] = 'b'

        # Marriage
        for v_family_handle in self.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_event_ref_list = v_family.__event_ref_list__

            for v_event_ref in v_event_ref_list:
                v_event = hkEventRef.EventRef(v_event_ref, self.__cursor__).get_event()
                v_media_list = v_event.__media_base__

                # 1 = Marriage, 2 = Marriage Settlement, 3 = Marriage License, 4 = Marriage Contract
                if (v_event.get_type() == hkGrampsDb.c_event_marriage or v_event.get_type() == hkGrampsDb.c_event_marriage_settlement or v_event.get_type() == hkGrampsDb.c_event_marriage_license or v_event.get_type() == hkGrampsDb.c_event_marriage_contract) and (len(v_media_list) > 0):
                    v_source_status['m'] = 'm'

        # Death / Burial
        v_media_list = []
        if hkGrampsDb.c_event_death in self.__person_event_dict__:  # Death
            v_event_list = self.__person_event_dict__[hkGrampsDb.c_event_death]
            v_event = v_event_list[0]
            v_media_list.extend(v_event.__media_base__)

        if hkGrampsDb.c_event_burial in self.__person_event_dict__:  # Burial
            v_event_list = self.__person_event_dict__[hkGrampsDb.c_event_burial]
            v_event = v_event_list[0]
            v_media_list.extend(v_event.__media_base__)

        if len(v_media_list) > 0:
            v_source_status['d'] = 'd'

        return v_source_status

    def get_birth_date(self):
        """
        Returns the birthdate in datetime.date format

        @return: v_birth_date: datetime.date
        """

        v_date: datetime.date = None

        if self.__birth_ref_index__ >= 0:
            v_event_ref = self.__event_ref_list__[self.__birth_ref_index__]
            v_event = hkEventRef.EventRef(v_event_ref, self.__cursor__).get_event()
            v_date = v_event.get_date().get_start_date()

        return v_date

    def get_death_date(self):
        """
        Returns the death date in datetime.date format

        @return: v_birth_date: datetime.date
        """

        v_date: datetime.date = None

        if self.__death_ref_index__ >= 0:
            v_event_ref = self.__event_ref_list__[self.__death_ref_index__]
            v_event = hkEventRef.EventRef(v_event_ref, self.__cursor__).get_event()
            v_date = v_event.get_date().get_start_date()

        return v_date

    def get_father(self):
        """
        Returns the handles of the father(s) of the current person

        @return: v_father_handles [str]
        """

        v_father_handle = None

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs, only returning first father..")

        if len(self.__parent_family_list__) > 0:
            v_family_handle = self.__parent_family_list__[0]
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_father_handle = v_family.get_father()

        return v_father_handle

    def get_mother(self):
        """
        Returns the handles of the mother(s) of the current person

        @return: v_mother_handles [str]
        """

        v_mother_handle = None

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs, only returning first mother..")

        if len(self.__parent_family_list__) > 0:
            v_family_handle = self.__parent_family_list__[0]
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_mother_handle = v_family.get_mother()

        return v_mother_handle

    def get_siblings(self):
        """
        Returns the handles of the sibling(s) of the current person

        @return: v_sibling_handles [str]
        """

        v_sibling_handles = []

        if len(self.__parent_family_list__) > 1:
            logging.warning("{} {} seems to have multiple parent pairs..")

        for v_family_handle in self.__parent_family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_children = v_family.get_children()
            v_children.remove(self.__handle__)
            v_sibling_handles = v_sibling_handles + v_children

        return v_sibling_handles

    def get_partners(self):
        """
        Returns the handles of the partner(s) of the current person

        @return: v_partner_handles [str]
        """

        v_partner_handles = []

        for v_family_handle in self.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_father_handle = v_family.get_father()
            v_mother_handle = v_family.get_mother()

            if v_father_handle == self.__handle__:
                v_partner_handles.append(v_mother_handle)
            else:
                v_partner_handles.append(v_father_handle)

        return v_partner_handles

    def get_children(self):
        """
        Returns the GrampsDB handles for all children

        @return: v_child_handles: [str]
        """

        v_child_handles = []

        for v_family_handle in self.__family_list__:
            v_family = hkFamily.Family(v_family_handle, self.__cursor__)
            v_child_handles = v_child_handles + v_family.get_children()

        return v_child_handles

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
        print("__alternate_name__: {}".format(self.__alternate_name__))
        print("__death_ref_index__: {}".format(self.__death_ref_index__))
        print("__birth_ref_index__: {}".format(self.__birth_ref_index__))
        print("__event_ref_list__: {}".format(self.__event_ref_list__))
        print("__family_list__: {}".format(self.__family_list__))
        print("__parent_family_list__: {}".format(self.__family_list__))
        print("__media_base__: {}".format(self.__media_base__))
        print("__address_base__: {}".format(self.__address_base__))
        print("__attribute_base__: {}".format(self.__attribute_base__))
        print("__url_base__: {}".format(self.__url_base__))
        # print("__lds_ord_base__: {}".format(self.__lds_ord_base__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_base__))
        print("__private__: {}".format(self.__private__))
        print("__person_ref_list__: {}".format(self.__person_ref_list__))
        print("*** End Person Log ***")
