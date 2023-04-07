import hkLanguage
import hkLatex 
import hkPerson

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu


class Ahnentafel:
    """A class to write an Ahnentafel chapter"""

    def __init__(self, p_subject_handle, p_cursor, p_document_path='../book/', p_source_status=False):
        self.__person_handle__ = p_subject_handle
        self.__cursor__ = p_cursor
        self.__document_path__ = p_document_path
        self.__chapter__ = None

        # Displays the status of sources to the Ahnentafel
        self.__source_status__ = p_source_status

        #  Create a generation list
        self.__generation_list__ = []
        self.__create_generation_list__(self.__person_handle__, 1)

    def __add_person(self, p_person_handle, p_binary_tree_string):
        v_person = hkPerson.Person(p_person_handle, self.__cursor__)

        # Display progress
        print("Adding: ", v_person.__given_names__, v_person.__surname__)

        v_pre_string = ''
        for v_index in range(1, len(p_binary_tree_string)):
            v_pre_string = v_pre_string + r'\quad\quad'

        v_string = v_pre_string + ' ' + p_binary_tree_string + r'\quad\quad ' + pu.escape_latex(v_person.__given_names__) + ' ' + pu.escape_latex(v_person.__surname__) + r'\newline'
        print(v_string)

        self.__chapter__.append(pl.NoEscape(v_string))

        v_father_handle = v_person.get_father()
        if v_father_handle is not None:
            self.__add_person(v_father_handle, p_binary_tree_string + 'M')
        else:
            print("End of tree...")

        v_mother_handle = v_person.get_mother()
        if v_mother_handle is not None:
            self.__add_person(v_mother_handle, p_binary_tree_string + 'F')
        else:
            print("End of tree...")

    def __add_generation(self, p_generation_list):
        """
        The Generation list consists of tuples (person_handle, binary_tree_string)
        """
        v_generation_index = len(p_generation_list[0][1]) + 1  # The generation index is determined using the length of the binary string
        v_next_generation_list = []

        if len(p_generation_list) > 0:
            v_generation_started = False
            for (v_person_handle, v_binary_tree_string) in p_generation_list:
                if v_person_handle is not None:
                    if not v_generation_started:
                        with self.__chapter__.create(pl.Section(numbering=False, title=hkLanguage.translate('generation') + ' ' + str(v_generation_index), label=False)):
                            v_generation_started = True
                            if self.__source_status__:
                                self.__chapter__.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth} | c | c | c |}%'))
                            else:
                                self.__chapter__.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth}}%'))

                    v_person = hkPerson.Person(v_person_handle, self.__cursor__)
                    v_source_status = v_person.__source_status__

                    if v_generation_index == 1:
                        v_new_binary_string = 'X'
                    elif v_person.__gender__ == 0:
                        v_new_binary_string = v_binary_tree_string + 'F'
                    elif v_person.__gender__ == 1:
                        v_new_binary_string = v_binary_tree_string + 'M'
                    else:
                        v_new_binary_string = v_binary_tree_string + '_'

                    if self.__source_status__:
                        # Research help: Add the source status to the Ahnentafel
                        self.__chapter__.append(pl.NoEscape(hkLatex.GetPersonNameWithReference(v_person.__given_names__, v_person.__surname__, v_person.__gramps_id__) + r' & ' + v_new_binary_string + r' & ' + v_source_status['b'] + r' & ' + v_source_status['m'] + r' & ' + v_source_status['d'] + r'\\'))
                    else:
                        self.__chapter__.append(pl.NoEscape(hkLatex.GetPersonNameWithReference(v_person.__given_names__, v_person.__surname__, v_person.__gramps_id__) + r' & ' + v_new_binary_string + r'\\'))

                    v_next_generation_list.append((v_person.get_father(), v_new_binary_string))
                    v_next_generation_list.append((v_person.get_mother(), v_new_binary_string))

            if v_generation_started:
                self.__chapter__.append(pl.NoEscape(r'\end{longtabu}%'))
                # v_generation_started = False

        if len(v_next_generation_list) > 0:
            self.__add_generation(v_next_generation_list)

    def __create_generation_list__(self, p_person_handle, p_generation_index):
        if p_person_handle is not None:
            v_person = hkPerson.Person(p_person_handle, self.__cursor__)

            # Add this person to the objects generation list
            self.__generation_list__.append((p_person_handle, p_generation_index))

            # Add siblings to the objects generation list
            v_sibling_handle_list = v_person.get_siblings()
            for v_sibling_handle in v_sibling_handle_list:
                if v_sibling_handle is not None:
                    self.__generation_list__.append(
                        (v_sibling_handle, p_generation_index))

            # Process the parents
            self.__create_generation_list__(v_person.get_father(), p_generation_index + 1)
            self.__create_generation_list__(v_person.get_mother(), p_generation_index + 1)

    def create_ahnentafel_chapter(self):
        """
        Writes the ahnentafel to a separate chapter in a subdocument
        """

        # v_subject = hpc.PersonChapter(self.__person_handle__, self.__cursor__, self.__document_path__)
        v_subject = hkPerson.Person(self.__person_handle__, self.__cursor__)

        # Display progress
        print("Writing the Ahnentafel...")

        # Create a new chapter for the active person
        self.__chapter__ = hkLatex.Chapter(title=hkLanguage.translate('pedigree of') + ' ' + v_subject.__given_names__ + ' ' + v_subject.__surname__, label=False)
        # self.__add_person(self.__person_handle__, 'X')
        self.__add_generation([(self.__person_handle__, '')])
        self.__chapter__.generate_tex(filepath=self.__document_path__ + 'Ahnentafel')
