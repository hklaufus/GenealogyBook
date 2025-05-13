import json


class Tag:
    __handle__: str = None
    __tag_name__: str = None
    __color__: str = None
    __priority__: int = None
    __change__: int = None

    def __init__(self, p_tag_handle: str, p_cursor):
        """
        Decode the GrampsDB event data for a given handle

        @param p_tag_handle: database handle to the relevant tag
        @param p_cursor: database cursor the database
        """

        p_cursor.execute('SELECT json_data FROM tag WHERE handle=?', [p_tag_handle])
        v_record = p_cursor.fetchone()

        if v_record is not None:
            v_json_data = v_record[0]

            if v_json_data is not None:
                v_decoder = json.JSONDecoder()
                v_tag_data = v_decoder.decode(v_json_data)

                self.__handle__ = v_tag_data['handle']
                self.__tag_name__ = v_tag_data['name']
                self.__color__ = v_tag_data['color']
                self.__priority__ = v_tag_data['priority']
                self.__change__ = v_tag_data['change']

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
