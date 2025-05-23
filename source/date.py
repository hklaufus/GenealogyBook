import calendar
import datetime

import gramps_db
import language


class Date:
    __calendar__: int = None
    __modifier__: int = None
    __quality__: int = None
    __dateval__: () = None
    __text__: str = None
    __sortval__: int = None
    __newyear__: int = None

    __date_1__: datetime.date = None
    __date_2__: datetime.date = None

    def __init__(self, p_gramps_date):
        """
        Decode the GrampsDB date information

        @param p_gramps_date:
        """

        if p_gramps_date is not None:
            self.__calendar__ = p_gramps_date['calendar']
            self.__modifier__ = p_gramps_date['modifier']
            self.__quality__ = p_gramps_date['quality']
            self.__dateval__ = p_gramps_date['dateval']
            self.__text__ = p_gramps_date['text']
            self.__sortval__ = p_gramps_date['sortval']
            self.__newyear__ = p_gramps_date['newyear']

            v_gramps_date_1 = list(self.__dateval__[0:4])

            if v_gramps_date_1[2] != 0:  # year set
                if v_gramps_date_1[0] == 0:  # day not set
                    v_gramps_date_1[0] = 1

                if v_gramps_date_1[1] == 0:  # month not set
                    v_gramps_date_1[1] = 1

                self.__date_1__ = datetime.date(v_gramps_date_1[2], v_gramps_date_1[1], v_gramps_date_1[0])

            if len(self.__dateval__) == 8:
                # Date range
                v_gramps_date_2 = list(self.__dateval__[4:8])

                if v_gramps_date_2[2] != 0:  # year set
                    if v_gramps_date_2[0] == 0:  # day not set
                        v_gramps_date_2[0] = 1

                    if v_gramps_date_2[1] == 0:  # month not set
                        v_gramps_date_2[1] = 1

                    self.__date_2__ = datetime.date(v_gramps_date_2[2], v_gramps_date_2[1], v_gramps_date_2[0])

    def get_start_date(self) -> datetime.date|None:
        """
        Returns the start date

        @return: datetime.date: __date_1__
        """

        return self.__date_1__

    def get_end_date(self) -> datetime.date|None:
        """
        Returns the end date

        @return: datetime.date: __date_2__
        """

        return self.__date_2__

    def get_mid_date(self) -> datetime.date|None:
        """
        Returns the mid-date of a time span, or the start date of en single date event

        @return: datetime.date: v_date
        """

        v_date = None
        if self.__date_1__ is not None:
            if self.__date_2__ is not None:
                v_time_delta = self.__date_2__ - self.__date_1__
                v_date = self.__date_1__ + v_time_delta / 2

                # Debug
                # print("self.__date_1__ / self.__date_1__ / v_date: {} / {} / {}".format(self.__date_1__, self.__date_2__, v_date))
            else:
                v_date = self.__date_1__

        return v_date

    def get_start_date_text(self, p_abbreviated: bool=True) -> str:
        """
        Returns the start date as text.

        @param p_abbreviated: bool
        @return: v_date_string: str
        """

        v_date_string: str = '-'

        if self.__date_1__ is not None:
            v_day1 = self.__date_1__.day
            v_month1 = self.__date_1__.month
            v_year1 = self.__date_1__.year

            v_month_string1 = calendar.month_name[v_month1]
            if p_abbreviated:
                v_month_string1 = calendar.month_abbr[v_month1]

            v_month_string1 = language.translate(v_month_string1)

            v_date_string = ((str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1)

        return v_date_string

    def __date_to_text__(self, p_abbreviated: bool=True) -> str:
        """
        Creates a human-readable string

        @param p_abbreviated:
        @return: v_date_string
        """

        v_modifier_set: set = {1, 2, 3}
        v_date_string: str = '-'

        if self.__date_1__ is not None:
            v_day_1: int = self.__date_1__.day
            v_month_1: int = self.__date_1__.month
            v_year_1: int = self.__date_1__.year

            v_month_string_1: str = calendar.month_name[v_month_1]
            if p_abbreviated:
                v_month_string_1 = calendar.month_abbr[v_month_1]

            v_month_string_1 = language.translate(v_month_string_1)

            if self.__date_2__ is not None:
                v_day_2: int = self.__date_2__.day
                v_month_2: int = self.__date_2__.month
                v_year_2: int = self.__date_2__.year

                v_month_string_2: str = calendar.month_name[v_month_2]
                if p_abbreviated:
                    v_month_string_2 = calendar.month_abbr[v_month_2]

                v_month_string_2 = language.translate(v_month_string_2)

                if self.__modifier__ == 4:
                    # Range
                    v_date_string = language.translate('between') + ' ' + ((str(v_day_1) + ' ') if v_day_1 != 0 else '') + v_month_string_1 + ' ' + str(v_year_1) + ' ' + language.translate('and') + ' ' + ((str(v_day_2) + ' ') if v_day_2 != 0 else '') + v_month_string_2 + ' ' + str(v_year_2)
                elif self.__modifier__ == 5:
                    # Span
                    v_date_string = language.translate('from') + ' ' + ((str(v_day_1) + ' ') if v_day_1 != 0 else '') + v_month_string_1 + ' ' + str(v_year_1) + ' ' + language.translate('until') + ' ' + ((str(v_day_2) + ' ') if v_day_2 != 0 else '') + v_month_string_2 + ' ' + str(v_year_2)
            else:
                if self.__modifier__ in v_modifier_set:
                    # Before, after, about
                    v_date_string = language.translate(gramps_db.c_date_modifier_dict[self.__modifier__]) + ' ' + ((str(v_day_1) + ' ') if v_day_1 != 0 else '') + v_month_string_1 + ' ' + str(v_year_1)
                else:
                    v_date_string = ((str(v_day_1) + ' ') if v_day_1 != 0 else '') + v_month_string_1 + ' ' + str(v_year_1)

        return v_date_string

    def __log__(self):
        print("*** Start Date Log ***")

        print("__calendar__: {}".format(self.__calendar__))
        print("__modifier__: {}".format(self.__modifier__))
        print("__quality__: {}".format(self.__quality__))
        print("__dateval__: {}".format(self.__dateval__))
        print("__text__: {}".format(self.__text__))
        print("__sortval__: {}".format(self.__sortval__))
        print("__newyear__: {}".format(self.__newyear__))

        print("__date_1__: {}".format(self.__date_1__))
        print("__date_2__: {}".format(self.__date_2__))
        print("*** End Date Log ***")
