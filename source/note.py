import json
import logging

import tag
import styled_text
import type


class Note:
    __note_handle__: str = None
    __note_gramps_id__: str = None
    __note_text__: styled_text.StyledText = None
    __note_format__: int = None
    __note_type__: type.Type = None
    __note_change__: int = None
    __note_tag_list__: list[tag.Tag] = None
    __note_private__: bool = None

    def __init__(self, p_note_handle, p_cursor):
        p_cursor.execute('SELECT json_data FROM note WHERE handle=?', [p_note_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]

            if v_json_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#9._Note
                v_decoder = json.JSONDecoder()
                v_note_data = v_decoder.decode(v_json_data)

                # Debug
                logging.debug('v_note_data: '.join(map(str, v_note_data)))

                self.__note_handle__ = v_note_data['handle']
                self.__note_gramps_id__ = v_note_data['gramps_id']
                self.__note_text__ = styled_text.StyledText(p_text=v_note_data['text'], p_cursor=p_cursor)
                self.__note_format__ = v_note_data['format']
                self.__note_type__ = type.Type(p_type=v_note_data['type'])
                self.__note_change__ = v_note_data['change']
                self.__note_tag_list__ = [tag.Tag(p_tag_handle=v_tag, p_cursor=p_cursor) for v_tag in v_note_data['tag_list']]
                self.__note_private__ = v_note_data['private']

    def get_text(self) -> str:
        return self.__note_text__.get_string()

    def __log__(self):
        """
        Print the contents of the note for debugging purposes.

        @return: None
        """

        print("*** Start Note Log ***")
        print("__note_handle__: {}".format(self.__note_handle__))
        print("__note_gramps_id__: {}".format(self.__note_gramps_id__))
        print("__note_text__: {}".format(self.__note_text__))
        print("__note_format__: {}".format(self.__note_format__))
        print("__note_type__: {}".format(self.__note_type__))
        print("__note_change__: {}".format(self.__note_change__))
        print("__note_tag_list__: {}".format(self.__note_tag_list__))
        print("__note_private__: {}".format(self.__note_private__))
        print("*** End Note Log ***")
