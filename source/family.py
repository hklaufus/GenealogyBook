import json

import child_ref
import event_ref
import gramps_db
import language
import note
import media_ref
import person
import tag


class Family:
    __handle__: str = None
    __gramps_id__: str = None
    __father_handle__: str = None
    __mother_handle__: str = None
    __child_ref_list__: list[child_ref.ChildRef]
    __type__: str = None
    __event_ref_list__: list[event_ref.EventRef] = None
    __media_list__: list[media_ref.MediaRef] = None
    __attribute_list__: [str] = None
    __citation_list__: [str] = None
    __note_list__: list[note.Note] = None
    __change__: int = None
    __tag_list__ = list[tag.Tag]
    __private__: bool = None

    def __init__(self, p_family_handle, p_cursor):
        """
        Decode the GrampsDB family data for a given handle

        @param p_family_handle: str
        @param p_cursor: database cursor
        """

        self.__cursor__ = p_cursor

        # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/family.py

        p_cursor.execute('SELECT json_data FROM family WHERE handle=?', [p_family_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]

            if v_json_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#2._Family:
                v_decoder = json.JSONDecoder()
                v_family_data = v_decoder.decode(v_json_data)

                self.__handle__ = v_family_data['handle']
                self.__gramps_id__ = v_family_data['gramps_id']
                self.__father_handle__ = v_family_data['father_handle']
                self.__mother_handle__ = v_family_data['mother_handle']
                self.__child_ref_list__ = [child_ref.ChildRef(p_person_ref=v_child, p_cursor=p_cursor) for v_child in v_family_data['child_ref_list']]
                self.__type__ = v_family_data['type']
                self.__event_ref_list__ = [event_ref.EventRef(p_event_ref=v_event, p_cursor=p_cursor) for v_event in v_family_data['event_ref_list']]
                self.__media_list__ = v_family_data['media_list']
                self.__attribute_list__ = v_family_data['attribute_list']
                # self.__lds_ord_base__ = v_family_data[9]
                self.__citation_list__ = v_family_data['citation_list']
                self.__note_list__ = v_family_data['note_list']
                self.__change__ = v_family_data['change']
                self.__tag_list__ = v_family_data['tag_list']
                self.__private__ = v_family_data['private']

    def get_father(self):
        v_father = None

        if self.__father_handle__ is not None:
            v_father = person.Person(p_person_handle=self.__father_handle__, p_cursor=self.__cursor__)

        return v_father

    def get_father_handle(self) -> str:
        return self.__father_handle__

    def get_mother(self):
        v_mother = None

        if self.__mother_handle__ is not None:
            v_mother = person.Person(p_person_handle=self.__mother_handle__, p_cursor=self.__cursor__)

        return v_mother

    def get_mother_handle(self) -> str:
        return self.__mother_handle__

    def get_children(self):
        v_child_list = [v_child_ref.get_child() for v_child_ref in self.__child_ref_list__]

        return v_child_list

    def get_child_ref_list(self) -> list[child_ref.ChildRef]:
        return self.__child_ref_list__

    def get_child_handle_list(self):
        v_child_handle_list = [v_child.get_child_handle() for v_child in self.__child_ref_list__]

        return v_child_handle_list

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

        for v_event_ref in self.__event_ref_list__:
            # v_event_ref = event_ref.EventRef(v_reference, self.__cursor__)

            if (p_role is None) or (v_event_ref.get_role() in v_use_role):
                v_event = v_event_ref.get_event()

                if len(v_event.__description__) == 0:
                    v_type_string = gramps_db.c_event_type_dict[v_event.get_type().get_value()]

                    v_father = self.get_father()
                    v_mother = self.get_mother()
                    v_name_string = v_father.__given_names__ + ' ' + v_father.__surname__ + " & " + v_mother.__given_names__ + ' ' + v_mother.__surname__

                    # v_date_place_string = '[' + v_event.get_place().__place_to_text__() + ', ' + v_event.get_date().__date_to_text__() + ']'
                    v_date_place_string = '['
                    if v_event.get_place() is not None:
                        v_place_string = v_event.get_place().__place_to_text__()
                        if len(v_place_string) > 0:
                            v_date_place_string = v_date_place_string + v_place_string + ', '

                    if v_event.get_date() is not None:
                        v_date_place_string = v_date_place_string + v_event.get_date().__date_to_text__() + ']'

                    v_event.__description__ = language.translate(v_type_string) + ' ' + v_name_string + ' ' + v_date_place_string

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
        print("__media_base__: {}".format(self.__media_list__))
        print("__attribute_base__: {}".format(self.__attribute_list__))
        # print("__lds_ord_base__: {}".format(self.__lds_ord_base__))
        print("__citation_base__: {}".format(self.__citation_list__))
        print("__note_base__: {}".format(self.__note_list__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_list__))
        print("__private__: {}".format(self.__private__))
        print("*** End Family Log ***")
