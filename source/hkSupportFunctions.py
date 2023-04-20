import hkGrampsDb
import hkLanguage

import calendar
import datetime
import logging
import math
import numpy

import pylatex as pl
import pylatex.utils as pu

# https://matplotlib.org/basemap/index.html
# from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
# import matplotlib.axes as axs
import matplotlib.figure as fig

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.geoaxes as cga

import os
import pandas

from PIL import Image

import hkPerson


def date_to_text(p_date_list, p_abbreviated=True):
    # v_modifier = 0
    v_modifier_set = {1, 2, 3}
    v_date_string = '-'

    if len(p_date_list) == 4:
        v_modifier = p_date_list[0]

        v_day1 = p_date_list[1]
        v_month1 = p_date_list[2]
        v_year1 = p_date_list[3]

        v_month_string1 = calendar.month_name[v_month1]
        if p_abbreviated:
            v_month_string1 = calendar.month_abbr[v_month1]

        v_month_string1 = hkLanguage.translate(v_month_string1)

        if v_modifier in v_modifier_set:
            # Before, after, about
            v_date_string = hkLanguage.translate(hkGrampsDb.c_date_modifier_dict[v_modifier]) + ' ' + ((str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1)
        else:
            v_date_string = ((str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1)

    elif len(p_date_list) == 7:
        v_modifier = p_date_list[0]

        v_day1 = p_date_list[1]
        v_month1 = p_date_list[2]
        v_year1 = p_date_list[3]

        v_month_string1 = calendar.month_name[v_month1]
        if p_abbreviated:
            v_month_string1 = calendar.month_abbr[v_month1]

        v_month_string1 = hkLanguage.translate(v_month_string1)

        v_day2 = p_date_list[4]
        v_month2 = p_date_list[5]
        v_year2 = p_date_list[6]

        v_month_string2 = calendar.month_name[v_month2]
        if p_abbreviated:
            v_month_string2 = calendar.month_abbr[v_month2]

        v_month_string2 = hkLanguage.translate(v_month_string2)

        if v_modifier == 4:
            # Range
            v_date_string = hkLanguage.translate('between') + ' ' + (
                (str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1) + ' ' + hkLanguage.translate(
                'and') + ' ' + ((str(v_day2) + ' ') if v_day2 != 0 else '') + v_month_string2 + ' ' + str(v_year2)
        elif v_modifier == 5:
            # Span
            v_date_string = hkLanguage.translate('from') + ' ' + (
                (str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1) + ' ' + hkLanguage.translate(
                'until') + ' ' + ((str(v_day2) + ' ') if v_day2 != 0 else '') + v_month_string2 + ' ' + str(v_year2)

    return v_date_string


def street_to_text(p_place_list, p_long_style=False):
    v_street_label = hkGrampsDb.c_place_type_dict[hkGrampsDb.c_place_type_street]

    v_string = ''
    if p_long_style:
        for v_place in p_place_list:
            v_string = v_string + ', ' + p_place_list[v_place][0]

        v_string = v_string[2:].strip()
    else:
        if v_street_label in p_place_list:
            v_string = v_string + p_place_list[v_street_label][0]

            v_place_string = place_to_text(p_place_list, p_long_style)
            if len(v_place_string) > 0:
                v_string = v_string + ', ' + v_place_string
        else:
            v_string = v_string + place_to_text(p_place_list, p_long_style)

    # Debug
    # logging.debug('p_place_list: '.join(map(str, p_place_list)))
    logging.debug('v_string = %s', v_string)

    return v_string


def sort_person_list_by_birth(p_person_handle_list, p_cursor):
    # Sort ID of persons in pPersonIdList by birth date

    # Debug
    # logging.debug('Before: '.join(map(str, p_person_handle_list)))

    # Retrieve person info
    v_new_person_list = []
    for v_person_handle in p_person_handle_list:
        v_person = hkPerson.Person(v_person_handle, p_cursor)
        v_birth_date = v_person.get_birth_date()
        v_new_person_list.append([v_birth_date, v_person_handle])

    f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0].year, x[0].month, x[0].day) if (x[0] is not None) else '-'
    v_new_person_list.sort(key=f_date_func)
    p_person_handle_list = [item[1] for item in v_new_person_list]

    # Debug
    # logging.debug('After: '.join(map(str, p_person_handle_list)))

    return p_person_handle_list


def picture_side_by_side_equal_height(p_chapter, p_image_path_1, p_image_path_2, p_image_title_1="", p_image_title_2="", p_image_rect_1=None, p_image_rect_2=None):
    """
    Positions two pictures side by side, scaling them such that their heights are equal.
    Zoom in on a focus area in case pImageRect_# is defined
    """

    # Latex Debug
    p_chapter.append(pl.NoEscape("% hkSupportFunctions.picture_side_by_side_equal_height"))

    c_gap = '3ex'  # 3ex gap between two pictures

    if p_image_rect_1 is None:
        p_chapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[scale=0.1]{"' + p_image_path_1 + r'"}}'))  # Added scale to prevent overflow in scalerel package
    else:
        v_left = '{' + str(p_image_rect_1[0] / 100) + r'\width}'
        v_right = '{' + str(1 - p_image_rect_1[2] / 100) + r'\width}'
        v_top = '{' + str(p_image_rect_1[1] / 100) + r'\height}'
        v_bottom = '{' + str(1 - p_image_rect_1[3] / 100) + r'\height}'

        # Debug
        logging.debug('pImageRect1: %s, %s, %s, %s', v_left, v_top, v_right, v_bottom)

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top

        p_chapter.append(pl.NoEscape(r'\def\imgA{\adjincludegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + p_image_path_1 + r'"}}'))

    if p_image_rect_2 is None:
        p_chapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + p_image_path_2 + r'"}}'))  # Added scale to prevent overflow in scalerel package
    else:
        v_left = '{' + str(p_image_rect_2[0] / 100) + r'\width}'
        v_right = '{' + str(1 - p_image_rect_2[2] / 100) + r'\width}'
        v_top = '{' + str(p_image_rect_2[1] / 100) + r'\height}'
        v_bottom = '{' + str(1 - p_image_rect_2[3] / 100) + r'\height}'

        # Debug
        logging.debug('pImageRect2: %s, %s, %s, %s', v_left, v_top, v_right, v_bottom)

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top

        p_chapter.append(pl.NoEscape(r'\def\imgB{\adjincludegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + p_image_path_2 + r'"}}'))

    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

    p_chapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))  # Scale imgA to the same height as reference imgB and output *both* images into a savebox
    p_chapter.append(pl.NoEscape(r'\widthImages=\wd\x'))  # Get the width of the scaled images
    p_chapter.append(pl.NoEscape(r'\widthAvailable=\dimexpr\textwidth-'+c_gap))  # Get the available width on the page for imgA and imgB
    p_chapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\widthAvailable}{\the\widthImages}'))  # Calculate the scale factor for the width
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))  # Scales imgA by scaleratio, and stores it in a horizontal box. Note: here the starred version of scalerel is used: this only outputs the scaled imgA
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_title_1) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}\kern'+c_gap))
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_title_2) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}'))
    # p_chapter.append(pl.NoEscape(r'\newline\newline'))
    p_chapter.append(pl.NoEscape(r'\vfill'))


def wrap_figure(p_chapter, p_filename, p_caption=None, p_position='i', p_width=r'0.50\textwidth', p_text='', p_zoom_rect=None):
    # This is a very ugly function, but what it does:
    # 1. It simplifies the use of the wrapfigure environment
    # 2. It fills the textblock with empty line in case the figure height is longer then the text block height.
    # This happens when the text block contains too little text lines, with the result that the next section heading and following text would overlap the figure

    # TODO: Move this to hkLatex in a pylatex format

    # Create a minipage
    # p_chapter.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

    # Set focus area 20220328
    v_figure = r'\includegraphics[width=' + p_width + r'-1ex]{"' + p_filename + r'"}'
    if p_zoom_rect is not None:
        v_left = '{' + str(p_zoom_rect[0] / 100) + r'\width}'
        v_right = '{' + str(1 - p_zoom_rect[2] / 100) + r'\width}'
        v_top = '{' + str(p_zoom_rect[1] / 100) + r'\height}'
        v_bottom = '{' + str(1 - p_zoom_rect[3] / 100) + r'\height}'
        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top
        v_figure = r'\adjincludegraphics[trim=' + v_trim + ', clip, width=' + p_width + r'-1ex]{"' + p_filename + r'"}'

    # Get the height of the figure
    p_chapter.append(pl.NoEscape(r'% Store the height of the photo in imageHeightA'))
    p_chapter.append(pl.NoEscape(r'\savebox{1}[' + p_width + r'][l]{' + v_figure + '}'))
    p_chapter.append(pl.NoEscape(r'\newdimen\imageheightA'))
    p_chapter.append(pl.NoEscape(r'\imageheightA=\ht1 \advance \imageheightA by \dp1'))

    # Get the height of the text block
    p_chapter.append(pl.NoEscape(r'% Store the height of the text box in textHeightA'))
    p_chapter.append(pl.NoEscape(r'\savebox{2}{\parbox{\textwidth-' + p_width + r'}{' + p_text + '}}'))
    p_chapter.append(pl.NoEscape(r'\newdimen\textheightA'))
    p_chapter.append(pl.NoEscape(r'\textheightA=\ht2 \advance \textheightA by \dp2'))

    p_chapter.append(pl.NoEscape(r'\makeatletter'))

    # Strip 'pt' from heights
    p_chapter.append(pl.NoEscape(r'% Strip "pt" from the heights and store heights in imageheightB and textheightB'))
    p_chapter.append(pl.NoEscape(r'\def\imageheightB{\strip@pt\imageheightA}'))
    p_chapter.append(pl.NoEscape(r'\def\textheightB{\strip@pt\textheightA}'))
    p_chapter.append(pl.NoEscape(r'\def\lineheight{\strip@pt\baselineskip}'))

    # Initialise variables
    p_chapter.append(pl.NoEscape(r'% Initialise variables'))
    p_chapter.append(pl.NoEscape(r'\def\deltaheight{0}'))
    p_chapter.append(pl.NoEscape(r'\def\remaininglines{0}'))

    # Calculate the remaining number of lines as a float
    p_chapter.append(pl.NoEscape(r'% Calculate the number of empty lines to add in order to prevent wrapfigure from wrapping the next section. Store in remaininglines'))
    p_chapter.append(pl.NoEscape(r'\FPsub{\deltaheight}{\imageheightB}{\textheightB}'))
    p_chapter.append(pl.NoEscape(r'\FPdiv{\remaininglines}{\deltaheight}{\lineheight}'))
    p_chapter.append(pl.NoEscape(r'\FPadd{\remaininglines}{\remaininglines}{1}'))
    p_chapter.append(pl.NoEscape(r'\FPround{\remaininglines}{\remaininglines}{0}'))

    p_chapter.append(pl.NoEscape(r'\makeatother'))

    # Calculate the remaining number of lines as an integer
    p_chapter.append(pl.NoEscape(r'% Store as integer'))
    p_chapter.append(pl.NoEscape(r'\setcounter{maxlines}{\intpart\remaininglines}'))
    p_chapter.append(pl.NoEscape(r'\addtocounter{maxlines}{1}'))

    # Add the figure and caption
    p_chapter.append(pl.NoEscape(r'\begin{wrapfigure}{' + p_position + '}{' + p_width + '}'))
    p_chapter.append(pl.NoEscape(r'\centering'))
    p_chapter.append(pl.NoEscape(r'\vspace{-1ex}'))
    p_chapter.append(pl.NoEscape(v_figure))
    if p_caption is not None:
        p_chapter.append(pl.NoEscape(r'\caption{' + pu.escape_latex(p_caption) + r'}'))
    p_chapter.append(pl.NoEscape(r'\end{wrapfigure}'))

    # Add the text
    p_chapter.append(pl.NoEscape(p_text))

    # Add the empty lines
    p_chapter.append(pl.NoEscape(r'% Add empty lines in order to prevent wrapfigure from wrapping the next section.'))
    p_chapter.append(pl.NoEscape(r'\setcounter{mycounter}{1}'))
    p_chapter.append(pl.NoEscape(r'\loop'))
    p_chapter.append(pl.NoEscape(r'\textcolor{white}{Empty line \\} % This is an empty line'))
    # p_chapter.append(pl.NoEscape(r'\\ % This is an empty line'))
    p_chapter.append(pl.NoEscape(r'\addtocounter{mycounter}{1}'))
    p_chapter.append(pl.NoEscape(r'\ifnum \value{mycounter}<\value{maxlines}'))
    p_chapter.append(pl.NoEscape(r'\repeat'))

    # End the minipage
    # p_chapter.append(pl.NoEscape(r'\end{minipage}'))
    # p_chapter.append(pl.NoEscape(r'\vfill'))


def create_map(p_document_path, p_country):
    # Check for existence of path
    if not os.path.exists(p_document_path):
        os.mkdir(p_document_path)

    # Create file name for figure
    v_file_path = os.path.join(p_document_path, 'Map_' + p_country + '.png')
    if not os.path.exists(v_file_path):
        # Get country latitude / longitudes
        v_coordinates = get_country_min_max_coordinates(p_country)
        v_lon_0 = v_coordinates[0]
        v_lat_0 = v_coordinates[1]
        v_lon_1 = v_coordinates[2]
        v_lat_1 = v_coordinates[3]

        # Draw map
        # v_figure = fig.Figure()
        # v_axes = cga.GeoAxes(rect=[0, 1, 0, 1], fig=v_figure, map_projection=ccrs.Mercator())
        v_axes = plt.axes(projection=ccrs.Mercator())
        v_axes.set_extent([v_lon_0, v_lon_1, v_lat_0, v_lat_1])
        v_axes.add_feature(cfeature.LAND.with_scale('10m'))  # , color='Bisque')
        v_axes.add_feature(cfeature.LAKES.with_scale('10m'), alpha=0.5)
        v_axes.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.2)
        v_axes.add_feature(cfeature.OCEAN.with_scale('10m'), linewidth=0.2)

        v_figure = v_axes.get_figure()
        # v_figure.show()
        v_figure.savefig(fname=v_file_path, bbox_inches='tight', pad_inches=0.0, transparent=True, dpi=500)
        plt.close(v_figure)

    return v_file_path


def get_country_min_max_coordinates(p_country_code):
    # Load list of Countries of the world from current working directory
    v_cwd = os.getcwd()
    v_file_path = os.path.join(v_cwd, 'cow.txt')
    v_data_frame = pandas.read_csv(v_file_path, sep=';', comment='#')

    # 20220109: Limit number of maps to Netherlands, Western Europe and the World
    if p_country_code == 'WEU':
        # Western Europe
        v_data_frame = v_data_frame.loc[v_data_frame['subregion'] == 'Western Europe', ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        v_min_max_list = [v_data_frame['min_lon'].min(), v_data_frame['min_lat'].min(), v_data_frame['max_lon'].max(), v_data_frame['max_lat'].max()]
    elif p_country_code == 'EUR':
        # Western Europe
        v_data_frame = v_data_frame.loc[v_data_frame['continent'] == 'Europe', ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        v_min_max_list = [v_data_frame['min_lon'].min(), v_data_frame['min_lat'].min(), v_data_frame['max_lon'].max(), v_data_frame['max_lat'].max()]
    elif p_country_code == 'WLD':
        # World
        v_min_max_list = [-179., -89., 179., 89.]
    else:
        v_data_frame = v_data_frame.loc[v_data_frame['adm0_a3'] == p_country_code, ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        v_min_max_list = v_data_frame.values.tolist()[0]

    # Debug
    logging.debug('get_country_min_max_coordinates: '.join(map(str, v_min_max_list)))

    return v_min_max_list


def get_country_continent_subregion(p_country_code):
    # Load list of Countries of the world from current working directory
    v_cwd = os.getcwd()
    v_file_path = os.path.join(v_cwd, 'cow.txt')
    v_data_frame = pandas.read_csv(v_file_path, sep=';', comment='#')

    v_data_frame = v_data_frame.loc[v_data_frame['adm0_a3'] == p_country_code, ['continent', 'subregion']]
    v_region_list = v_data_frame.values.tolist()[0]

    # Debug
    logging.debug('get_country_continent_subregion: '.join(map(str, v_region_list)))

    return v_region_list


def round_up(p_value, p_decimals=0):
    v_multiplier = 10 ** p_decimals
    return math.ceil(p_value * v_multiplier) / v_multiplier


def round_down(p_value, p_decimals=0):
    v_multiplier = 10 ** p_decimals
    return math.floor(p_value * v_multiplier) / v_multiplier

def gramps_date_to_python_date(p_date):
    """
    Converts a Gramps date format to a python date

    @param p_date: list: [DD, MM, YYYY]
    @return: date as python object otherwise none
    """

    # Debug
    # print("p_date = {}".format(p_date))

    if isinstance(p_date, list):
        if p_date[0] == 0:  # day not set
            p_date[0] = 1

        if p_date[1] == 0:  # month not set
            p_date[1] = 1

        v_date = datetime.date(p_date[2], p_date[1], p_date[0])
    else:
        v_date = None

    return v_date
