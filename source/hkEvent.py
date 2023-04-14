import pickle
import hkDate
import hkMedia
import hkNote
import hkPlace
import hkTag


class Event:
    __handle__: str = None
    __gramps_id__: str = None
    __type__: int = None
    __date_base__: [hkDate.Date] = None
    __description__: str = None
    __place__: str = None
    __citation_base__: [str] = None
    __note_base__: [hkNote.Note] = None
    __media_base__: [hkMedia.Media] = None
    __attribute_base__: [str] = None
    __change__: int = None
    __tag_base__: [hkTag.Tag] = None
    __private__: bool = None

    def __init__(self, p_event_handle, p_cursor):
        """
        Decode the GrampsDB event data for a given handle

        @param p_event_handle: database handle to the relevant event
        @param p_cursor: database cursor the database
        """

        p_cursor.execute('SELECT blob_data FROM event WHERE handle=?', [p_event_handle])
        v_blob_data = p_cursor.fetchone()
        if v_blob_data is not None:
            v_event_data = pickle.loads(v_blob_data[0])

            v_place_handle = v_event_data[5]
            if v_place_handle is not None:
                self.__event_place__ = hkPlace.Place(v_place_handle, p_cursor)  # TODO: remove in favour of __place__

            self.__cursor__ = p_cursor

            self.__handle__ = v_event_data[0]
            self.__gramps_id__ = v_event_data[1]
            self.__type__ = v_event_data[2]
            self.__date_base__ = v_event_data[3]
            self.__description__ = v_event_data[4]
            self.__place__ = v_event_data[5]
            self.__citation_base__ = v_event_data[6]
            self.__note_base__ = v_event_data[7]
            self.__media_base__ = v_event_data[8]
            self.__attribute_base__ = v_event_data[9]
            self.__change__ = v_event_data[10]
            self.__tag_base__ = v_event_data[11]
            self.__private__ = v_event_data[12]

    def get_type(self):
        """
        Returns the event type.

        @return: self.__type__
        """

        return self.__type__[0]  # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py

    def get_place(self):
        """
        Returns the event place.

        @return: v_place: hkPlace.Place object
        """

        v_place = None
        if (self.__place__ is not None) and (len(self.__place__) > 0):
            v_place = hkPlace.Place(self.__place__, self.__cursor__)

        return v_place

    def get_date(self):
        """
        Returns the event date(s).

        @return: v_date: hkDate.Date object
        """

        v_date = hkDate.Date(self.__date_base__)

        return v_date

    def get_description(self):
        """
        Returns the event description.

        @return: self.__description__: str
        """

        return self.__description__

    def __log__(self):
        """
        Print the contents of the event for debugging purposes.

        @return: None
        """

        print("*** Start Event Log ***")
        # print("__event_place__: {}".format(self.__event_place__.__log__()))
        # print("__event_media_list__: {}".format(self.__event_media_list__))

        print("__handle__: {}".format(self.__handle__))
        print("__gramps_id__: {}".format(self.__gramps_id__))
        print("__type__: {}".format(self.__type__))
        print("__date_base__: {}".format(self.__date_base__))
        print("__description__: {}".format(self.__description__))
        print("__place__: {}".format(self.__place__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__media_base__: {}".format(self.__media_base__))
        print("__attribute_base__: {}".format(self.__attribute_base__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_base__))
        print("__private__: {}".format(self.__private__))
        print("*** End Event Log ***")
