import date

class PlaceName:
    __date__: date.Date = None
    __lang__: str = None
    __value__: str = None

    def __init__(self, p_place_name):
        """
        Decode the GrampsDB place data for a given handle

        @param p_place_handle: database handle to the relevant place
        @param p_cursor: database cursor the database
        """

        self.__date__ = date.Date(p_gramps_date=p_place_name['date'])
        self.__lang__ = p_place_name['lang']
        self.__value__ = p_place_name['value']

    def get_value(self):
        return self.__value__

    def get_language(self):
        return self.__lang__

    def get_date(self):
        return self.__date__