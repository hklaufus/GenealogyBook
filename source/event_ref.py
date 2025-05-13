import event
import note
import type


class EventRef:
    __private__: bool = None
    __note_list__: list[note.Note] = None
    __attribute_list__: list[str] = None
    __ref__: str = None
    __role__: type.Type = None

    def __init__(self, p_event_ref, p_cursor):
        self.__cursor__ = p_cursor

        self.__private__ = p_event_ref['private']
        self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in p_event_ref['note_list']]
        self.__attribute_list__ = p_event_ref['attribute_list']
        self.__ref__ = p_event_ref['ref']
        self.__role__ = type.Type(p_event_ref['role'])

    def __log__(self):
        """
        Print the contents of the event ref for debugging purposes.

        @return: None
        """

        print("*** Start Event Ref Log ***")
        print("__privacy_base__: {}".format(self.__private__))
        print("__note_base__: {}".format(self.__note_list__))
        print("__attribute_base__: {}".format(self.__attribute_list__))
        print("__ref_base__: {}".format(self.__ref__))
        print("__role__: {}".format(self.__role__))
        print("*** End Event Ref Log ***")

    def get_event(self):
        return event.Event(self.__ref__, self.__cursor__)

    def get_role(self) -> type.Type|None:
        """
        Return the value indicating the role

        @return: v_role: int
        """

        v_role: type.Type|None = None
        if self.__role__ is not None:
            v_role = self.__role__

        return v_role
