import hkEvent


class EventRef:
    __privacy_base__: bool = None
    __note_base__: [str] = None
    __attribute_base__: [str] = None
    __ref_base__: str = None
    __role__: (int, str) = None

    def __init__(self, p_event_ref, p_cursor):
        self.__cursor__ = p_cursor

        self.__privacy_base__ = p_event_ref[0]
        self.__note_base__ = p_event_ref[1]
        self.__attribute_base__ = p_event_ref[2]
        self.__ref_base__ = p_event_ref[3]
        self.__role__ = p_event_ref[4]

    def __log__(self):
        """
        Print the contents of the event ref for debugging purposes.

        @return: None
        """

        print("*** Start Event Ref Log ***")
        print("__privacy_base__: {}".format(self.__privacy_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__attribute_base__: {}".format(self.__attribute_base__))
        print("__ref_base__: {}".format(self.__ref_base__))
        print("__role__: {}".format(self.__role__))
        print("*** End Event Ref Log ***")

    def get_event(self):
        return hkEvent.Event(self.__ref_base__, self.__cursor__)
