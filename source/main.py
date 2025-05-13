import logging
import sqlite3

import gen_book

def main():
    # Set logging level
    # log.basicConfig(filename='debug.log', format='%(module)s:%(funcName)s:%(levelname)s:%(message)s', level=log.WARNING)
    logging.basicConfig(format='%(module)s:%(funcName)s:%(levelname)s:%(message)s', level=logging.INFO)

    v_connection = sqlite3.connect('file:../db/sqlite.db?mode=ro', uri=True)
    v_cursor = v_connection.cursor()

    v_book = gen_book.Book()
    v_book.write_main_document(v_cursor)

    v_connection.close()


if __name__ == "__main__":
    main()
