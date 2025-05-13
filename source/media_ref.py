import media
import note


class MediaRef:
    __ref__: str = None
    __private__: bool = None
    __citation_list__: str = None
    __note_list__: list[note.Note] = None
    __attribute_list__: str = None
    __rect__: str = None

    def __init__(self, p_media_ref, p_cursor):
        self.__cursor__ = p_cursor

        self.__ref__ = p_media_ref['ref']
        self.__private__ = p_media_ref['private']
        self.__citation_list__ = p_media_ref['citation_list']
        self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in p_media_ref['note_list']]
        self.__attribute_list__ = p_media_ref['attribute_list']
        self.__rect__ = p_media_ref['rect']

    def __log__(self):
        """
        Print the contents of the person ref for debugging purposes.

        @return: None
        """

        print("*** Start Media Ref Log ***")
        print("__ref__: {}".format(self.__ref__))
        print("__privacy__: {}".format(self.__private__))
        print("__citation_list__: {}".format(self.__citation_list__))
        print("__note_list__: {}".format(self.__note_list__))
        print("__attribute_list__: {}".format(self.__attribute_list__))
        print("__rect__: {}".format(self.__rect__))
        print("*** End Media Ref Log ***")

    def get_media(self):
        return media.Media(p_media_handle=self.__ref__, p_cursor=self.__cursor__)

    def get_rect(self):
        return self.__rect__