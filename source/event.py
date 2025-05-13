import json

import date
import event_type
import media_ref
import note
import place
import tag


class Event:
    __handle__: str = None
    __gramps_id__: str = None
    __type__: event_type.EventType = None
    __date__: date.Date = None
    __description__: str = None
    __place__: place.Place | None= None
    __citation_list__: [str] = None
    __note_list__: list[note.Note] = None
    __media_list__: list[media_ref.MediaRef] = None
    __attribute_list__: [str] = None
    __change__: int = None
    __tag_list__: list[tag.Tag] = None
    __private__: bool = None

    def __init__(self, p_event_handle, p_cursor):
        """
        Decode the GrampsDB event data for a given handle

        @param p_event_handle: database handle to the relevant event
        @param p_cursor: database cursor the database
        """

        self.__cursor__ = p_cursor

        p_cursor.execute('SELECT json_data FROM event WHERE handle=?', [p_event_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]

            if v_json_data is not None:
                v_decoder = json.JSONDecoder()
                v_event_data = v_decoder.decode(v_json_data)

                self.__handle__ = v_event_data['handle']
                self.__gramps_id__ = v_event_data['gramps_id']
                self.__type__ = event_type.EventType(p_type=v_event_data['type'])
                self.__date__ = date.Date(p_gramps_date=v_event_data['date'])
                self.__description__ = v_event_data['description']
                self.__citation_list__ = v_event_data['citation_list']
                self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in v_event_data['note_list']]
                self.__media_list__ = [media_ref.MediaRef(p_media_ref=v_media_ref, p_cursor=p_cursor) for v_media_ref in v_event_data['media_list']]
                self.__attribute_list__ = v_event_data['attribute_list']
                self.__change__ = v_event_data['change']
                self.__tag_list__ = [tag.Tag(p_tag_handle=v_tag, p_cursor=p_cursor) for v_tag in v_event_data['tag_list']]
                self.__private__ = v_event_data['private']

                if v_event_data['place'] is None:
                    self.__place__ = None
                elif len(v_event_data['place']) == 0:
                    self.__place__ = None
                else:
                    self.__place__ = place.Place(p_place_handle=v_event_data['place'], p_cursor=p_cursor)


    def get_event_type(self) -> event_type.EventType:
        """
        Returns the event type.

        :return:
        """

        return self.get_type()

    def get_type(self) -> event_type.EventType:
        """
        Returns the event type.

        @return: self.__type__
        """

        # https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/eventtype.py
        return self.__type__

    def get_place(self) -> place.Place:
        """
        Returns the event place.

        @return: v_place
        """

        return self.__place__

    def get_date(self) -> date.Date:
        """
        Returns the event date(s).

        @return: self.__date__
        """

        return self.__date__

    def get_description(self) -> str:
        """
        Returns the event description.

        @return: self.__description__
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
        print("__date_base__: {}".format(self.__date__))
        print("__description__: {}".format(self.__description__))
        print("__place__: {}".format(self.__place__))
        print("__citation_base__: {}".format(self.__citation_list__))
        print("__note_base__: {}".format(self.__note_list__))
        print("__media_base__: {}".format(self.__media_list__))
        print("__attribute_base__: {}".format(self.__attribute_list__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_list__))
        print("__private__: {}".format(self.__private__))
        print("*** End Event Log ***")
