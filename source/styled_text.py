import logging

import tag


class StyledText:
    __string__: str = None
    __tag_list__: str = None

    def __init__(self, p_text: dict, p_cursor):
        self.__string__ = p_text['string']
        self.__tag_list__ = p_text['tags'] # [tag.Tag(p_tag_handle=v_tag, p_cursor=p_cursor) for v_tag in p_text['tags']]

    def __log__(self):
        """
        Print the contents of the styled text for debugging purposes.

        @return: None
        """

        logging.debug("*** Start Styled Text Log ***")
        logging.debug("__string__: {}".format(self.__string__))
        logging.debug("*** End Styled Text ***")

    def get_string(self):
        return self.__string__


