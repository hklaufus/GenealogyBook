import hkLanguage as hlg
import hkPersonChapter as hpc
import hkGrampsDb as hgd
import hkLatex as hlt

# https://jeltef.github.io/PyLaTeX/current/index.html
import pylatex as pl
import pylatex.utils as pu
import pylatex.base_classes.containers as pbc


class Ahnentafel:
    """A class to write an Ahnentafel chapter"""

    def __init__(self, p_subject_handle, p_cursor, p_document_path='../book/', p_source_status=False):
        self.__person_handle = p_subject_handle
        self.__cursor = p_cursor
        self.__document_path = p_document_path

        # Displays the status of sources to the Ahnentafel
        self.__source_status = p_source_status

        #  Create a generation list
        self.__generation_list = []
        self.__create_generation_list(self.__person_handle, 1)

    @property
    def generation_list(self):
        return self.__generation_list

    def __add_person(self, p_person_handle, p_binary_tree_string):
        v_person = hpc.Person(p_person_handle, self.__cursor, self.__document_path)

        # Display progress
        print("Adding: ", v_person.given_names, v_person.surname)

        v_pre_string = ''
        for v_index in range(1, len(p_binary_tree_string)):
            v_pre_string = v_pre_string + r'\quad\quad'

        v_string = v_pre_string + ' ' + p_binary_tree_string + r'\quad\quad ' + pu.escape_latex(v_person.given_names) + ' ' + pu.escape_latex(v_person.surname) + r'\newline'
        print(v_string)

        self.__Chapter.append(pl.NoEscape(v_string))

        v_father_handle = v_person.father_handle
        if v_father_handle is not None:
            self.__add_person(v_father_handle, p_binary_tree_string + 'M')
        else:
            print("End of tree...")

        v_mother_handle = v_person.mother_handle
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
        # v_section = None

        if len(p_generation_list) > 0:
            v_generation_started = False
            for (v_person_handle, v_binary_tree_string) in p_generation_list:
                if v_person_handle is not None:
                    if not v_generation_started:
                        with self.__Chapter.create(pl.Section(numbering=False, title=hlg.translate('generation') + ' ' + str(v_generation_index), label=False)):
                            v_generation_started = True
                            if self.__source_status:
                                self.__Chapter.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth} | c | c | c |}%'))
                            else:
                                self.__Chapter.append(pl.NoEscape(r'\begin{longtabu}{p{\dimexpr.7\textwidth} p{\dimexpr.3\textwidth}}%'))

                    v_person = hpc.Person(v_person_handle, self.__cursor, self.__document_path)
                    v_source_status = v_person.source_status

                    v_new_binary_string = ''
                    if v_generation_index == 1:
                        v_new_binary_string = 'X'
                    elif v_person.gender == 0:
                        v_new_binary_string = v_binary_tree_string + 'F'
                    elif v_person.gender == 1:
                        v_new_binary_string = v_binary_tree_string + 'M'
                    else:
                        v_new_binary_string = v_binary_tree_string + '_'

                    if self.__source_status:
                        # Research help: Add the source status to the Ahnentafel
                        self.__Chapter.append(pl.NoEscape(hlt.GetPersonNameWithReference(v_person.given_names, v_person.surname, v_person.gramps_id) + r' & ' + v_new_binary_string + r' & ' + v_source_status['b'] + r' & ' + v_source_status['m'] + r' & ' + v_source_status['d'] + r'\\'))
                    else:
                        self.__Chapter.append(pl.NoEscape(hlt.GetPersonNameWithReference(v_person.given_names, v_person.surname, v_person.gramps_id) + r' & ' + v_new_binary_string + r'\\'))

                    v_next_generation_list.append((v_person.father_handle, v_new_binary_string))
                    v_next_generation_list.append((v_person.mother_handle, v_new_binary_string))

            if v_generation_started:
                self.__Chapter.append(pl.NoEscape(r'\end{longtabu}%'))
                v_generation_started = False

        if len(v_next_generation_list) > 0:
            self.__add_generation(v_next_generation_list)

    def __create_generation_list(self, p_person_handle, p_generation_index):
        if p_person_handle is not None:
            v_person = hpc.Person(p_person_handle, self.__cursor, self.__document_path)

            # Add this person to the objects generation list
            self.__generation_list.append((p_person_handle, p_generation_index))

            # Add siblings to the objects generation list
            v_sibling_handle_list = hgd.get_sibling_handles_old(p_person_handle, self.__cursor)
            for v_sibling_handle in v_sibling_handle_list:
                if v_sibling_handle is not None:
                    self.__generation_list.append(
                        (v_sibling_handle, p_generation_index))

            # Process the parents
            self.__create_generation_list(v_person.father_handle, p_generation_index + 1)
            self.__create_generation_list(v_person.mother_handle, p_generation_index + 1)

    def create_ahnentafel_chapter(self):
        """
        Writes the ahnentafel to a separate chapter in a subdocument
        """

        v_subject = hpc.Person(self.__person_handle, self.__cursor, self.__document_path)

        # Display progress
        print("Writing the Ahnentafel...")

        # Create a new chapter for the active person
        self.__Chapter = hlt.Chapter(title=hlg.translate('pedigree of') + ' ' + v_subject.given_names + ' ' + v_subject.surname, label=False)
        # self.__add_person(self.__person_handle, 'X')
        self.__add_generation([(self.__person_handle, '')])
        self.__Chapter.generate_tex(filepath=self.__document_path + 'Ahnentafel')
