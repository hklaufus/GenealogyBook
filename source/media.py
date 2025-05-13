import json
import pathlib
import pickle

import date
import note
import tag


class Media:
    __handle__: str = None
    __gramps_id__: str = None
    __media_path__: str = None
    __mime__: str = None
    __description__: str = None
    __checksum__: str = None
    __attribute_list__: list[str] = None
    __citation_list__: list[str] = None
    __note_list__: list[note.Note] = None
    __change__: int = None
    __date__: list[date.Date] = None
    __tag_list__: list[tag.Tag] = None
    __private__: bool = None

    def __init__(self, p_media_handle, p_cursor):
        """
        Decode the GrampsDB media data for a given handle

        @param p_media_handle:
        @param p_cursor:
        """

        # See: https://github.com/gramps-project/gramps/blob/47f392ef70618cfece86e5210c19c2c1a768a4e0/gramps/gen/lib/media.py

        self.__cursor__ = p_cursor

        p_cursor.execute('SELECT json_data FROM media WHERE handle=?', [p_media_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]

            if v_json_data is not None:
                v_decoder = json.JSONDecoder()
                v_media_data = v_decoder.decode(v_record[0])

                self.__handle__ = v_media_data['handle']
                self.__gramps_id__ = v_media_data['gramps_id']
                self.__media_path__ = v_media_data['path']
                self.__mime__ = v_media_data['mime']
                self.__description__ = v_media_data['desc']
                self.__checksum__ = v_media_data['checksum']
                self.__attribute_list__ = v_media_data['attribute_list']
                self.__citation_list__ = v_media_data['citation_list']
                self.__note_list__ = [note.Note(p_note_handle=v_note, p_cursor=p_cursor) for v_note in v_media_data['note_list']]
                self.__change__ = v_media_data['change']
                self.__date__ = v_media_data['date']
                self.__tag_list__ = [tag.Tag(p_tag_handle=v_tag, p_cursor=p_cursor) for v_tag in v_media_data['tag_list']]
                self.__private__ = v_media_data['private']

                # Check whether path is relative or absolute
                v_path_object = pathlib.Path(self.__media_path__)
                if not v_path_object.is_absolute():
                    # Relative path, add base path
                    v_base_path = self.__get_media_base_path__()
                    v_path_object = pathlib.Path.joinpath(pathlib.Path(v_base_path), v_path_object)

                self.__media_path__ = str(v_path_object.as_posix())

    def __get_media_base_path__(self):
        """
        Retrieve the media base path from the GrampsDb

        @return: v_base_path: str
        """

        self.__cursor__.execute('SELECT value FROM metadata WHERE setting=?', ['media-path'])
        v_blob_data = self.__cursor__.fetchone()

        v_base_path = ''
        if v_blob_data is not None:
            v_base_path = pickle.loads(v_blob_data[0])

        return v_base_path

    def get_media_tag_names(self):
        v_media_tag_names = []
        for v_tag in self.__tag_list__:
            v_media_tag_names.append(v_tag.__tag_name__)

        return v_media_tag_names

    def tag_name_in_media_tag_names(self, p_tag_name):
        v_result: bool = False

        if p_tag_name in self.get_media_tag_names():
            v_result = True

        return v_result

    def __log__(self):
        """
        Print the contents of the media for debugging purposes.

        @return: None
        """

        print("*** Start Media Log ***")
        print("__handle__: {}".format(self.__handle__))
        print("__gramps_id__: {}".format(self.__gramps_id__))
        print("__media_path__: {}".format(self.__media_path__))
        print("__mime__: {}".format(self.__mime__))
        print("__description__: {}".format(self.__description__))
        print("__checksum__: {}".format(self.__checksum__))
        print("__attribute_base__: {}".format(self.__attribute_list__))
        print("__citation_base__: {}".format(self.__citation_list__))
        print("__note_base__: {}".format(self.__note_list__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_list__))
        print("__private__: {}".format(self.__private__))
        print("*** End Media Log ***")
