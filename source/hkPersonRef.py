import hkPerson


class PersonRef:
    def __init__(self, p_person_ref, p_cursor):
        self.__cursor__ = p_cursor

        self.__privacy_base__ = p_person_ref[0]
        self.__citation_base__ = p_person_ref[1]
        self.__note_base__ = p_person_ref[2]
        self.__ref_base__ = p_person_ref[3]
        self.__rel__ = p_person_ref[4]

    def __log__(self):
        """
        Print the contents of the person ref for debugging purposes.

        @return: None
        """

        print("*** Start Person Ref Log ***")
        print("__privacy_base__: {}".format(self.__privacy_base__))
        print("__citation_base__: {}".format(self.__citation_base__))
        print("__note_base__: {}".format(self.__note_base__))
        print("__ref_base__: {}".format(self.__ref_base__))
        print("__rel__: {}".format(self.__rel__))
        print("*** End Person Ref Log ***")

    def get_person(self):
        return hkPerson.Person(self.__ref_base__, self.__cursor__)
