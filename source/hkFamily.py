import hkEventRef
import hkGrampsDb
import hkLanguage
import hkPerson
import hkPersonRef

import pickle


class Family:
    def __init__(self, p_family_handle, p_cursor):
        """
        Decode the GrampsDB family data for a given handle

        @param p_family_handle: str
        @param p_cursor: database cursor
        """

        self.__cursor__ = p_cursor

        # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/family.py

        p_cursor.execute('SELECT blob_data, gramps_id, father_handle, mother_handle FROM family WHERE handle=?', [p_family_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_blob_data = v_record[0]

            if v_blob_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#2._Family:
                v_family_data = pickle.loads(v_blob_data)

                self.__handle__ = v_family_data[0]
                self.__gramps_id__ = v_family_data[1]
                self.__father_handle__ = v_family_data[2]
                self.__mother_handle__ = v_family_data[3]
                self.__child_ref_list__ = v_family_data[4]
                self.__type__ = v_family_data[5]
                self.__event_ref_list__ = v_family_data[6]
                self.__media_base__ = v_family_data[7]
                self.__attribute_base__ = v_family_data[8]
                # self.__lds_ord_base__ = v_family_data[9]
                self.__citation_base__ = v_family_data[10]
                self.__note_base__ = v_family_data[11]
                self.__change__ = v_family_data[12]
                self.__tag_base__ = v_family_data[13]
                self.__private__ = v_family_data[14]

    def get_father(self):
        return self.__father_handle__

    def get_mother(self):
        return self.__mother_handle__

    def get_children(self):
        v_child_handles = []

        for v_reference in self.__child_ref_list__:
            v_child_ref = hkPersonRef.PersonRef(v_reference, self.__cursor__)
            v_child = v_child_ref.get_person()

            v_child_handles.append(v_child.__handle__)

        return v_child_handles

    def get_events(self, p_type=None, p_role=None):
        """
        Creates a generator list object

        @param: p_type: set of types to filter on
        @param: p_role: set of roles to filter on

        @return: v_event
        """

        # Convert parameters to set
        if (p_type is not None) and isinstance(p_type, int):
            v_use_type = {p_type}
        else:
            v_use_type = p_type

        if (p_role is not None) and isinstance(p_role, int):
            v_use_role = {p_role}
        else:
            v_use_role = p_role

        for v_reference in self.__event_ref_list__:
            v_event_ref = hkEventRef.EventRef(v_reference, self.__cursor__)

            if (p_role is None) or (v_event_ref.get_role() in v_use_role):
                v_event = v_event_ref.get_event()

                if len(v_event.__description__) == 0:
                    v_type_string = hkGrampsDb.c_event_type_dict[v_event.get_type()]

                    v_father = hkPerson.Person(self.get_father(), self.__cursor__)
                    v_mother = hkPerson.Person(self.get_mother(), self.__cursor__)
                    v_name_string = v_father.__given_names__ + ' ' + v_father.__surname__ + " & " + v_mother.__given_names__ + ' ' + v_mother.__surname__

                    # v_date_place_string = '[' + v_event.get_place().__place_to_text__() + ', ' + v_event.get_date().__date_to_text__() + ']'
                    v_date_place_string = '['
                    if v_event.get_place() is not None:
                        v_place_string = v_event.get_place().__place_to_text__()
                        if len(v_place_string) > 0:
                            v_date_place_string = v_date_place_string + v_place_string + ', '

                    if v_event.get_date() is not None:
                        v_date_place_string = v_date_place_string + v_event.get_date().__date_to_text__() + ']'

                    v_event.__description__ = hkLanguage.translate(v_type_string) + ' ' + v_name_string + ' ' + v_date_place_string

                if (p_type is None) or (v_event.get_type() in v_use_type):
                    yield v_event

    def __log__(self):
        """
        Print the contents of the family for debugging purposes.

        @return: None
        """

        print("*** Start Family Log ***")
        print("__handle__: {}".format(self.__handle__))
        print("__gramps_id__: {}".format(self.__gramps_id__))
        print("__father_handle__: {}".format(self.__father_handle__))
        print("__mother_handle__: {}".format(self.__mother_handle__))
        print("__child_ref_list__: {}".format(self.__child_ref_list__))
        print("__type__: {}".format(self.__type__))
        print("__event_ref_list__: {}".format(self.__event_ref_list__))
        print("__media_base__: {}".format(self.__media_base__))
        print("__attribute_base__: {}".format(self.__attribute_base__))
        # print("__lds_ord_base__: {}".format(self.__lds_ord_base__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_base__))
        print("__private__: {}".format(self.__private__))
        print("*** End Family Log ***")
