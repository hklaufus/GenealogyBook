import inspect
import logging
import pickle

import hkGrampsDb
import hkNote
import hkTag


class Place:
    __enclosed_by__: str = ''
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

        p_cursor.execute('SELECT enclosed_by, blob_data FROM place WHERE handle=?', [p_place_handle])
        v_return_value = p_cursor.fetchone()
        if v_return_value is not None:
            v_enclosed_by = v_return_value[0]
            v_blob_data = v_return_value[1]
            v_place_data = pickle.loads(v_blob_data)

            self.__enclosed_by__ = v_enclosed_by

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

            if len(self.__place_name__) == 0:
                logging.warning("__place_name__ is empty for handle: {}".format(p_place_handle))

        # self.__log__()

    def __create_place_dict__(self):
        """
        Creates a dictionary of the hierarchy of a given place by recursively retrieving data of its enclosing places

        @return: v_place_dict
        """
        v_place_dict = {}

        v_enclosed_by = self.__enclosed_by__
        v_place_dict[self.get_type()] = self.__handle__

        while len(v_enclosed_by) > 0:
            v_place = Place(v_enclosed_by, self.__cursor__)

            v_enclosed_by = v_place.__enclosed_by__
            v_place_dict[v_place.get_type()] = v_place.__handle__

        return v_place_dict

    def get_type(self):
        """
        Return the type of the place

        @return: self.__place_type__[0]
        """

        v_return_value = -1

        if isinstance(self.__place_type__, tuple):
            v_return_value = self.__place_type__[0]
        elif isinstance(self.__place_type__, int):
            v_return_value = self.__place_type__
        else:
            logging.warning("Unknown place type: {}".format(self.__place_type__))

        return v_return_value

    def get_place_name(self):
        """
        Returns the place name

        @return: v_place_name: str
        """

        v_place_name = None

        if isinstance(self.__place_name__, str):
            v_place_name = self.__place_name__
        elif isinstance(self.__place_name__, tuple):
            v_place_name = self.__place_name__[0]
        else:
            logging.warning("Check type of self.__place_name: {}".format(self.__place_name__))

        return v_place_name

    def get_location(self, p_place_type):
        """
        Returns the location

        @param: p_place_type: int. Code for type of place. Refer to hkGramps.
        @return: v_place: hkPlace
        """

        v_place = None

        v_enclosed_by = self.__enclosed_by__
        v_type = self.get_type()

        while (v_type != p_place_type) and (len(v_enclosed_by) > 0):
            v_place = Place(v_enclosed_by, self.__cursor__)
            v_enclosed_by = v_place.__enclosed_by__
            v_type = v_place.get_type()

        return v_place

    def get_country(self):
        """
        Returns the city

        @return: v_place: hkPlace
        """

        v_place = self.get_location(hkGrampsDb.c_place_type_country)

        return v_place

    def get_city(self):
        """
        Returns the city

        @return: v_place: hkPlace
        """

        v_place = self.get_location(hkGrampsDb.c_place_type_city)
        if v_place is None:
            v_place = self.get_location(hkGrampsDb.c_place_type_town)
        if v_place is None:
            v_place = self.get_location(hkGrampsDb.c_place_type_village)
        if v_place is None:
            v_place = self.get_location(hkGrampsDb.c_place_type_municipality)

        return v_place

    def get_street(self):
        """
        Returns the city

        @return: v_place: hkPlace
        """

        v_place = self.get_location(hkGrampsDb.c_place_type_street)

        return v_place

    def __street_to_text__(self, p_long_style=False):
        """
        Returns the name of the street.

        :param p_long_style: Boolean. If True, recursively add names of higher hierarchy levels
        :return: v_string: str.
        """

        v_place_type = hkGrampsDb.c_place_type_street

        return self.__location_to_text__(v_place_type, p_long_style)

    def __city_to_text__(self, p_long_style=False):
        """
        Returns the name of the city / town / village / municipality.

        :param p_long_style: Boolean. If True, recursively add names of higher hierarchy levels
        :return: v_string: str.
        """

        v_string = self.__location_to_text__(hkGrampsDb.c_place_type_city, p_long_style)

        if len(v_string) == 0:
            v_string = self.__location_to_text__(hkGrampsDb.c_place_type_town, p_long_style)

        if len(v_string) == 0:
            v_string = self.__location_to_text__(hkGrampsDb.c_place_type_village, p_long_style)

        if len(v_string) == 0:
            v_string = self.__location_to_text__(hkGrampsDb.c_place_type_municipality, p_long_style)

        return v_string

    def __country_to_text__(self, p_long_style=False):
        """
        Returns the name of the country.

        @param: p_long_style: Boolean. If True, recursively add names of higher hierarchy levels
        @return: v_string: str.

        """

        v_place_type = hkGrampsDb.c_place_type_country

        return self.__location_to_text__(v_place_type, p_long_style)

    def __location_to_text__(self, p_place_type, p_long_style=False):
        """
        Returns the name of the location

        @param: p_place_type: int. Code for type of place. Refer to hkGramps.
        @param: p_long_style: Boolean. If True, recursively add names of higher hierarchy levels
        @return: v_string: str.
        """

        v_string = ''

        if p_place_type is not None:
            v_place_dict = self.__create_place_dict__()

            if p_place_type in v_place_dict:
                v_place = Place(v_place_dict[p_place_type], self.__cursor__)
                v_type = v_place.get_type()
                v_enclosed_by = v_place.__enclosed_by__

                v_string = v_string + v_place.__place_name__[0]

                if p_long_style:
                    while (v_type != p_place_type) and (len(v_enclosed_by) > 0):
                        v_place = Place(v_enclosed_by, self.__cursor__)
                        v_type = v_place.get_type()
                        v_enclosed_by = v_place.__enclosed_by__
                        v_string = v_string + ', ' + v_place.__place_name__[0]
        else:
            logging.warning("Invalid p_place_type: {}".format(p_place_type))

        return v_string.strip()

    def __place_to_text__(self, p_long_style=False):
        """
        Returns the name of the city / town / village / municipality.

        :param p_long_style: Boolean. If True, recursively add names of higher hierarchy levels
        :return: v_string: str.
        """

        v_string = ''
        if len(self.__place_name__) == 0:
            print("This function: {}".format(inspect.stack()[1][3]))
            print("Calling function: {}".format(inspect.stack()[2][3]))
            logging.warning("__place_name__ is empty for GrampsId: {}..".format(self.__gramps_id__))
        else:
            v_enclosed_by = self.__enclosed_by__
            v_string = self.__place_name__[0]

            if p_long_style:
                while len(v_enclosed_by) > 0:
                    v_place = Place(v_enclosed_by, self.__cursor__)
                    v_enclosed_by = v_place.__enclosed_by__
                    v_string = v_string + ', ' + v_place.__place_name__[0]

        return v_string.strip()

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
