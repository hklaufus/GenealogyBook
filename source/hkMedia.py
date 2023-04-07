import pathlib
import pickle

import hkDate
import hkNote
import hkTag


class Media:
    __handle__: str = None
    __gramps_id__: str = None
    __media_path__: str = None
    __mime__: str = None
    __description__: str = None
    __checksum__: str = None
    __attribute_base__: [str] = None
    __citation_base__: [str] = None
    __note_base__: [hkNote.Note] = None
    __change__: int = None
    __date_base__: [hkDate.Date] = None
    __tag_base__: [hkTag.Tag] = None
    __private__: bool = None

    def __init__(self, p_media_handle, p_cursor):
        """
        Decode the GrampsDB media data for a given handle

        @param p_media_handle:
        @param p_cursor:
        """

        # See: https://github.com/gramps-project/gramps/blob/47f392ef70618cfece86e5210c19c2c1a768a4e0/gramps/gen/lib/media.py

        self.__cursor__ = p_cursor

        p_cursor.execute('SELECT blob_data FROM media WHERE handle=?', [p_media_handle])
        v_blob_data = p_cursor.fetchone()
        if v_blob_data is not None:
            v_media_data = pickle.loads(v_blob_data[0])

            self.__handle__ = v_media_data[0]
            self.__gramps_id__ = v_media_data[1]
            self.__media_path__ = v_media_data[2]
            self.__mime__ = v_media_data[3]
            self.__description__ = v_media_data[4]
            self.__checksum__ = v_media_data[5]
            self.__attribute_base__ = v_media_data[6]
            self.__citation_base__ = v_media_data[7]
            self.__note_base__ = v_media_data[8]
            self.__change__ = v_media_data[9]
            self.__date_base__ = v_media_data[10]
            self.__tag_base__ = v_media_data[11]
            self.__private__ = v_media_data[12]

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
        for v_tag_handle in self.__tag_base__:
            v_tag = hkTag.Tag(v_tag_handle, self.__cursor__)
            v_media_tag_names.append(v_tag.__tag_name__)

        return v_media_tag_names

    def tag_name_in_media_tag_names(self, p_tag_name):
        v_value: bool = False

        if p_tag_name in self.get_media_tag_names():
            v_value = True

        return v_value

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
        print("__attribute_base__: {}".format(self.__attribute_base__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_base__))
        print("__private__: {}".format(self.__private__))
        print("*** End Media Log ***")
