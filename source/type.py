import logging


class Type:
    __string__: str = None
    __value__: int = None

    def __init__(self, p_type: dict):
        self.__string = p_type['string']
        self.__value__ = p_type['value']

    def __log__(self):
        """
        Print the contents of the event ref for debugging purposes.

        @return: None
        """

        logging.debug("*** Start Type Log ***")
        logging.debug("__string__: {}".format(self.__string__))
        logging.debug("__value__: {}".format(self.__value__))
        logging.debug("*** End Type Log ***")

    def get_value(self):
        return self.__value__

    def get_string(self):
        return self.__string__

