import logging

import note
import person
import type


class ChildRef:
    __ref__: str = None
    __private__: bool = None
    __citation_list__: str = None
    __note_list__: list[note.Note] = None
    __frel__: type.Type = None
    __mrel__: type.Type = None

    def __init__(self, p_person_ref, p_cursor):
        self.__cursor__ = p_cursor

        self.__ref__ = p_person_ref['ref']
        self.__private__ = p_person_ref['private']
        self.__citation_list__ = p_person_ref['citation_list']
        self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in p_person_ref['note_list']]
        self.__frel__ = type.Type(p_type=p_person_ref['frel'])
        self.__mrel__ = type.Type(p_type=p_person_ref['mrel'])

    def __log__(self):
        """
        Print the contents of the person ref for debugging purposes.

        @return: None
        """

        logging.debug("*** Start Child Ref Log ***")
        logging.debug("__privacy_base__: {}".format(self.__private__))
        logging.debug("__citation_base__: {}".format(self.__citation_list__))
        logging.debug("__note_base__: {}".format(self.__note_list__))
        logging.debug("__ref_base__: {}".format(self.__ref__))
        logging.debug("__frel__: {}".format(self.__frel__))
        logging.debug("__mrel__: {}".format(self.__mrel__))
        logging.debug("*** End Child Ref Log ***")

    def get_child_handle(self):
        return self.__ref__

    def get_child(self):
        return person.Person(p_person_handle=self.__ref__, p_cursor=self.__cursor__)
