import pickle

import hkGrampsDb
import hkNote
import hkTag

class Place:
    __handle__: str = ''
    __gramps_id__: str = ''
    __title__: str = ''
    __longitude__: float = 0.
    __latitude__: float = 0.
    __place_ref_list__: [str] = None
    __place_name__: str = ''
    __alt_names__: [str] = None
    __place_type__: int = 0
    __place_code__: str = ''
    __alt_loc__: [str] = None
    __url_base__: str = ''
    __media_base__: str = None
    __citation_base__: [str] = None
    __note_base__: [hkNote.Note] = None
    __change__: int = None
    __tag_base__: [hkTag.Tag] = None
    __private__: bool = None

    def __init__(self, p_place_handle, p_cursor):
        """
        Decode the GrampsDB place data for a given handle

        @param p_place_handle: database handle to the relevant place
        @param p_cursor: database cursor the database
        """

        # See https://github.com/gramps-project/gramps/blob/master/gramps/gen/lib/place.py

        self.__cursor__ = p_cursor

        p_cursor.execute('SELECT blob_data FROM place WHERE handle=?', [p_place_handle])
        v_blob_data = p_cursor.fetchone()
        if v_blob_data is not None:
            v_place_data = pickle.loads(v_blob_data[0])

            self.__handle__ = v_place_data[0]
            self.__gramps_id__ = v_place_data[1]
            self.__title__ = v_place_data[2]
            self.__longitude__ = v_place_data[3]
            self.__latitude__ = v_place_data[4]
            self.__place_ref_list__ = v_place_data[5]
            self.__place_name__ = v_place_data[6]
            self.__alt_names__ = v_place_data[7]
            self.__place_type__ = v_place_data[8]
            self.__place_code__ = v_place_data[9]
            self.__alt_loc__ = v_place_data[10]
            self.__url_base__ = v_place_data[11]
            self.__media_base__ = v_place_data[12]
            self.__citation_base__ = v_place_data[13]
            self.__note_base__ = v_place_data[14]
            self.__change__ = v_place_data[15]
            self.__tag_base__ = v_place_data[16]
            self.__private__ = v_place_data[17]

    def __create_place_dict__(self):
        v_place_dict = {}

        v_place_handle = self.__handle__
        while len(v_place_handle) > 0:
            self.__cursor__.execute('SELECT enclosed_by, blob_data FROM place WHERE handle=?', [v_place_handle])
            v_record = self.__cursor__.fetchone()
            if v_record is not None:
                v_place_handle = v_record[0]
                v_blob_data = v_record[1]
                v_place_data = pickle.loads(v_blob_data)

                if len(v_place_data[3]) == 0:
                    v_place_longitude = 0.
                else:
                    v_place_longitude = float(v_place_data[3])

                if len(v_place_data[4]) == 0:
                    v_place_latitude = 0.
                else:
                    v_place_latitude = float(v_place_data[4])

                v_place_name = v_place_data[6][0]
                v_place_type = hkGrampsDb.c_place_type_dict[v_place_data[8][0]]
                v_place_code = v_place_data[9]

                v_place_dict[v_place_type] = [v_place_name, (v_place_latitude, v_place_longitude), v_place_code]

        return v_place_dict

    def __street_to_text__(self, p_long_style=False):
        v_street_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_street]

        v_place_dict = self.__create_place_dict__()

        v_string = ''
        if p_long_style:
            for v_place in v_place_dict:
                v_string = v_string + ', ' + v_place_dict[v_place][0]

            v_string = v_string[2:].strip()
        else:
            if v_street_label in v_place_dict:
                v_string = v_string + v_place_dict[v_street_label][0]

                v_place_string = self.__place_to_text__(p_long_style)
                if len(v_place_string) > 0:
                    v_string = v_string + ', ' + v_place_string
            else:
                v_string = v_string + self.__place_to_text__(p_long_style)

        return v_string

    def __place_to_text__(self, p_long_style=False):
        v_city_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_city]
        v_town_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_town]
        v_village_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_village]
        v_municipality_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_municipality]

        v_place_dict = self.__create_place_dict__()

        v_string = ''
        if p_long_style:
            for v_place in v_place_dict:
                v_string = v_string + ', ' + v_place_dict[v_place][0]

            v_string = v_string[2:].strip()
        else:
            v_found = True
            if v_city_label in v_place_dict:
                v_string = v_string + v_place_dict[v_city_label][0]
            elif v_town_label in v_place_dict:
                v_string = v_string + v_place_dict[v_town_label][0]
            elif v_village_label in v_place_dict:
                v_string = v_string + v_place_dict[v_village_label][0]
            elif v_municipality_label in v_place_dict:
                v_string = v_string + v_place_dict[v_municipality_label][0]
            else:
                v_found = False

            if v_found:
                v_country_string = self.__country_to_text__(p_long_style)
                if len(v_country_string) > 0:
                    v_string = v_string + ', ' + v_country_string
            else:
                v_string = v_string + self.__country_to_text__(p_long_style)

        return v_string

    def __country_to_text__(self, p_long_style=False):
        v_country_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_country]

        v_place_dict = self.__create_place_dict__()

        v_string = ''
        if p_long_style:
            for v_place in v_place_dict:
                v_string = v_string + ', ' + v_place_dict[v_place][0]

            v_string = v_string[2:].strip()
        else:
            if v_country_label in v_place_dict:
                v_string = v_string + v_place_dict[v_country_label][0]

        return v_string

    def __log__(self):
        """
        Print the contents of the place for debugging purposes.

        @return: None
        """

        print("*** Start Place Log ***")
        print("__handle__: {}".format(self.__handle__))
        print("__gramps_id__: {}".format(self.__gramps_id__))
        print("__title__: {}".format(self.__title__))
        print("__longitude__: {}".format(self.__longitude__))
        print("__latitude__: {}".format(self.__latitude__))
        print("__place_ref_list__: {}".format(self.__place_ref_list__))
        print("__place_name__: {}".format(self.__place_name__))
        print("__alt_names__: {}".format(self.__alt_names__))
        print("__place_type__: {}".format(self.__place_type__))
        print("__place_code__: {}".format(self.__place_code__))
        print("__alt_loc__: {}".format(self.__alt_loc__))
        print("__url_base__: {}".format(self.__url_base__))
        print("__media_base__: {}".format(self.__media_base__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__change__: {}".format(self.__change__))
        print("__tag_base__: {}".format(self.__tag_base__))
        print("__private__: {}".format(self.__private__))
        print("*** End Place Log ***")
