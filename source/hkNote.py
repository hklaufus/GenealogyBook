import pickle

import hkTag


class Note:
    __note_handle__: str = None
    __note_gramps_id__: str = None
    __note_text__: str = None
    __note_format__: int = None
    __note_type__: int = None
    __note_change__: int = None
    __note_tag_base__: [hkTag.Tag] = None
    __note_private__: bool = None

    def __init__(self, p_note_handle, p_cursor):
        p_cursor.execute('SELECT blob_data FROM note WHERE handle=?', [p_note_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_blob_data = v_record[0]

            if v_blob_data is not None:
                # See https://www.gramps-project.org/wiki/index.php/Using_database_API#9._Note
                v_note_data = pickle.loads(v_blob_data)

                # Debug
                # logging.debug('v_note_data: '.join(map(str, v_note_data)))

                self.__note_handle__ = v_note_data[0]
                self.__note_gramps_id__ = v_note_data[1]
                self.__note_text__ = v_note_data[2][0]
                self.__note_format__ = v_note_data[3]
                self.__note_type__ = v_note_data[4][0]
                self.__note_change__ = v_note_data[5]
                self.__note_tag_base__ = v_note_data[6]
                self.__note_private__ = v_note_data[7]

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
        print("__note_tag_base__: {}".format(self.__note_tag_base__))
        print("__note_private__: {}".format(self.__note_private__))
        print("*** End Note Log ***")
