import pickle


class Tag:
    __handle__: str = ''
    __tag_name__: str = ''
    __color__: str = ''
    __priority__: int = 0
    __change__: int = 0

    def __init__(self, p_tag_handle, p_cursor):
        """
        Decode the GrampsDB event data for a given handle

        @param p_tag_handle: database handle to the relevant tag
        @param p_cursor: database cursor the database
        """

        p_cursor.execute('SELECT blob_data FROM tag WHERE handle=?', [p_tag_handle])
        v_blob_data = p_cursor.fetchone()
        if v_blob_data is not None:
            v_tag_data = pickle.loads(v_blob_data[0])

            self.__handle__ = v_tag_data[0]
            self.__tag_name__ = v_tag_data[1]
            self.__color__ = v_tag_data[2]
            self.__priority__ = v_tag_data[3]
            self.__change__ = v_tag_data[4]

    def __log__(self):
        """
        Print the contents of the tag for debugging purposes.

        @return: None
        """

        print("*** Start Tag Log ***")
        print("__handle__: {}".format(self.__handle__))
        print("__tag_name__: {}".format(self.__tag_name__))
        print("__color__: {}".format(self.__color__))
        print("__priority__: {}".format(self.__priority__))
        print("__change__: {}".format(self.__change__))
        print("*** End Tag Log ***")
