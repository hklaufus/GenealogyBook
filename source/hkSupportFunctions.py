import hkGrampsDb as hgd
import hkLanguage as hkl

import calendar
import logging

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
import pandas as pd

from PIL import Image


def get_start_date(p_date_list, p_abbreviated=True):
    v_date_string = '-'

    if (len(p_date_list) == 4) or (len(p_date_list) == 7):
        v_day1 = p_date_list[1]
        v_month1 = p_date_list[2]
        v_year1 = p_date_list[3]

        v_month_string1 = calendar.month_name[v_month1]
        if p_abbreviated:
            v_month_string1 = calendar.month_abbr[v_month1]

        v_month_string1 = hkl.translate(v_month_string1)

        v_date_string = ((str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1)

    return v_date_string


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

        v_month_string1 = hkl.translate(v_month_string1)

        if v_modifier in v_modifier_set:
            # Before, after, about
            v_date_string = hkl.translate(hgd.c_date_modifier_dict[v_modifier]) + ' ' + (
                (str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1)
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

        v_month_string1 = hkl.translate(v_month_string1)

        v_day2 = p_date_list[4]
        v_month2 = p_date_list[5]
        v_year2 = p_date_list[6]

        v_month_string2 = calendar.month_name[v_month2]
        if p_abbreviated:
            v_month_string2 = calendar.month_abbr[v_month2]

        v_month_string2 = hkl.translate(v_month_string2)

        if v_modifier == 4:
            # Range
            v_date_string = hkl.translate('between') + ' ' + (
                (str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1) + ' ' + hkl.translate(
                'and') + ' ' + ((str(v_day2) + ' ') if v_day2 != 0 else '') + v_month_string2 + ' ' + str(v_year2)
        elif v_modifier == 5:
            # Span
            v_date_string = hkl.translate('from') + ' ' + (
                (str(v_day1) + ' ') if v_day1 != 0 else '') + v_month_string1 + ' ' + str(v_year1) + ' ' + hkl.translate(
                'until') + ' ' + ((str(v_day2) + ' ') if v_day2 != 0 else '') + v_month_string2 + ' ' + str(v_year2)

    return v_date_string


def street_to_text(p_place_list, p_long_style=False):
    v_street_label = hgd.c_place_type_dict[hgd.c_place_type_street]

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


def place_to_text(p_place_list, p_long_style=False):
    v_city_label = hgd.c_place_type_dict[hgd.c_place_type_city]
    v_town_label = hgd.c_place_type_dict[hgd.c_place_type_town]
    v_village_label = hgd.c_place_type_dict[hgd.c_place_type_village]
    v_municipality_label = hgd.c_place_type_dict[hgd.c_place_type_municipality]

    v_string = ''
    if p_long_style:
        for v_place in p_place_list:
            v_string = v_string + ', ' + p_place_list[v_place][0]

        v_string = v_string[2:].strip()
    else:
        v_found = True
        if v_city_label in p_place_list:
            v_string = v_string + p_place_list[v_city_label][0]
        elif v_town_label in p_place_list:
            v_string = v_string + p_place_list[v_town_label][0]
        elif v_village_label in p_place_list:
            v_string = v_string + p_place_list[v_village_label][0]
        elif v_municipality_label in p_place_list:
            v_string = v_string + p_place_list[v_municipality_label][0]
        else:
            v_found = False

        if v_found:
            v_country_string = country_to_text(p_place_list, p_long_style)
            if len(v_country_string) > 0:
                v_string = v_string + ', ' + v_country_string
        else:
            v_string = v_string + country_to_text(p_place_list, p_long_style)

    # Debug
    # logging.debug('p_place_list: '.join(map(str, p_place_list)))
    logging.debug('v_string = %s', v_string)

    return v_string


def country_to_text(p_place_list, p_long_style=False):
    v_country_label = hgd.c_place_type_dict[hgd.c_place_type_country]

    v_string = ''
    if p_long_style:
        for v_place in p_place_list:
            v_string = v_string + ', ' + p_place_list[v_place][0]

        v_string = v_string[2:].strip()
    else:
        if v_country_label in p_place_list:
            v_string = v_string + p_place_list[v_country_label][0]

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
        v_person_data = hgd.decode_person_data(v_person_handle, p_cursor)
        v_birth_ref_index = v_person_data[6]
        if v_birth_ref_index >= 0:
            v_event_ref_list = v_person_data[7]
            v_birth_event_ref = v_event_ref_list[v_birth_ref_index]
            v_birth_event_handle = v_birth_event_ref[3]
            v_birth_event_info = hgd.decode_event_data(v_birth_event_handle, p_cursor)
            v_birth_date = v_birth_event_info[1]
        else:
            v_birth_date = '-'

        v_new_person_list.append([v_birth_date, v_person_handle])

    f_date_func = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
    v_new_person_list.sort(key=f_date_func)
    p_person_handle_list = [item[1] for item in v_new_person_list]

    # Debug
    # logging.debug('After: '.join(map(str, p_person_handle_list)))

    return p_person_handle_list


def picture_side_by_side_equal_height(p_chapter, p_image_path_1, p_image_path_2, p_image_title_1="", p_image_title_2="", p_image_rect_1=None, p_image_rect_2=None):
    """
    Positions two pictures side by side, scaling them such that thier heights are equal.
    Zoom in on a focus area in case pImageRect_# is defined
    """

    # Latex Debug
    p_chapter.append(pl.NoEscape("% hkSupportFunctions.picture_side_by_side_equal_height"))

    if p_image_rect_1 is None:
        p_chapter.append(pl.NoEscape(
            r'\def\imgA{\includegraphics[scale=0.1]{"' + p_image_path_1 + r'"}}'))  # Added scale to prevent overflow in scalerel package
    else:
        v_left = '{' + str(p_image_rect_1[0] / 100) + r'\wd1}'
        v_right = '{' + str(1 - p_image_rect_1[2] / 100) + r'\wd1}'
        v_top = '{' + str(p_image_rect_1[1] / 100) + r'\ht1}'
        v_bottom = '{' + str(1 - p_image_rect_1[3] / 100) + r'\ht1}'

        # Debug
        logging.debug('pImageRect1: %s, %s, %s, %s', v_left, v_top, v_right, v_bottom)

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top

        p_chapter.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + p_image_path_1 + r'"}}'))
        p_chapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + p_image_path_1 + r'"}}'))

    if p_image_rect_2 is None:
        p_chapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + p_image_path_2 + r'"}}'))  # Added scale to prevent overflow in scalerel package
    else:
        v_left = '{' + str(p_image_rect_2[0] / 100) + r'\wd2}'
        v_right = '{' + str(1 - p_image_rect_2[2] / 100) + r'\wd2}'
        v_top = '{' + str(p_image_rect_2[1] / 100) + r'\ht2}'
        v_bottom = '{' + str(1 - p_image_rect_2[3] / 100) + r'\ht2}'

        # Debug
        logging.debug('pImageRect2: %s, %s, %s, %s', v_left, v_top, v_right, v_bottom)

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top

        p_chapter.append(pl.NoEscape(r'\sbox2{\includegraphics{"' + p_image_path_2 + r'"}}'))
        p_chapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[trim=' + v_trim + ', clip, scale=0.1]{"' + p_image_path_2 + r'"}}'))

    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

    p_chapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))
    p_chapter.append(pl.NoEscape(r'\imgwidthA=\wd\x'))
    p_chapter.append(pl.NoEscape(r'\textwidthA=\dimexpr\textwidth-5ex'))
    p_chapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\textwidthA}{\the\imgwidthA}'))
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_title_1) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}\kern3ex'))
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_title_2) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}'))
    # p_chapter.append(pl.NoEscape(r'\newline\newline'))
    p_chapter.append(pl.NoEscape(r'\vfill'))


def picture_side_by_side_equal_height_old(p_chapter, p_image_data_1, p_image_data_2):
    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

    p_chapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[scale=0.1]{"' + p_image_data_1[2] + r'"}}'))  # Added scale to prevent overflow in scalerel package
    p_chapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + p_image_data_2[2] + r'"}}'))
    p_chapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))
    p_chapter.append(pl.NoEscape(r'\imgwidthA=\wd\x'))
    p_chapter.append(pl.NoEscape(r'\textwidthA=\dimexpr\textwidth-5ex'))
    p_chapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\textwidthA}{\the\imgwidthA}'))
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_data_1[4]) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}\kern3ex'))
    p_chapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
    p_chapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    p_chapter.append(pl.NoEscape(r'\box0'))
    p_chapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(p_image_data_2[4]) + '}'))
    p_chapter.append(pl.NoEscape(r'\end{minipage}'))
    p_chapter.append(pl.NoEscape(r'\newline\newline'))


def wrap_figure_new(p_chapter, p_filename, p_caption=None, p_position='i', p_width=r'0.50\textwidth', p_text='', p_zoom_rect=None):
    # This is a very ugly function, but what it does:
    # 1. It simplifies the use of the wrapfigure environment
    # 2. It fills the textblock with empty line in case the figure height is longer then the text block height.
    # This happens when the text block contains too little text lines, with the result that the next section heading and following text would overlap the figure

    # TODO: Move this to hkLatex in a pylatex format

    # Create a minipage
    p_chapter.append(pl.NoEscape(r'\begin{minipage}{\textwidth}'))

    # Set focus area 20220328
    v_trim = ''
    if p_zoom_rect is not None:
        v_left = '{' + str(p_zoom_rect[0] / 100) + r'\wd1}'
        v_right = '{' + str(1 - p_zoom_rect[2] / 100) + r'\wd1}'
        v_top = '{' + str(p_zoom_rect[1] / 100) + r'\ht1}'
        v_bottom = '{' + str(1 - p_zoom_rect[3] / 100) + r'\ht1}'

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top
        p_chapter.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + p_filename + r'"}}'))

    # Add the figure
    p_chapter.append(pl.NoEscape(r'\begin{wrapfigure}{' + p_position + '}{' + p_width + '}'))
    p_chapter.append(pl.NoEscape(r'\centering'))
    p_chapter.append(pl.NoEscape(r'\vspace{-1em}'))

    if p_zoom_rect is not None:
        p_chapter.append(pl.NoEscape(r'\includegraphics[trim=' + v_trim + ', clip, width=' + p_width + r'-1em]{"' + p_filename + r'"}'))
    else:
        p_chapter.append(pl.NoEscape(r'\includegraphics[width=' + p_width + r'-1em]{"' + p_filename + r'"}'))

    if p_caption is not None:
        p_chapter.append(pl.NoEscape(r'\caption{' + pu.escape_latex(p_caption) + r'}'))

    p_chapter.append(pl.NoEscape(r'\end{wrapfigure}'))

    # Add the text
    p_chapter.append(pl.NoEscape(p_text))

    # end the minipage
    p_chapter.append(pl.NoEscape(r'\end{minipage}'))
    p_chapter.append(pl.NoEscape(r'\vfill'))


def wrap_figure(p_chapter, p_filename, p_caption=None, p_position='i', p_width=r'0.50\textwidth', p_text='', p_zoom_rect=None):
    # This is a very ugly function, but what it does:
    # 1. It simplifies the use of the wrapfigure environment
    # 2. It fills the textblock with empty line in case the figure height is longer then the text block height.
    # This happens when the text block contains too little text lines, with the result that the next section heading and following text would overlap the figure

    # Set focus area 20220328
    v_trim = ''
    if p_zoom_rect is not None:
        v_left = '{' + str(p_zoom_rect[0] / 100) + r'\wd1}'
        v_right = '{' + str(1 - p_zoom_rect[2] / 100) + r'\wd1}'
        v_top = '{' + str(p_zoom_rect[1] / 100) + r'\ht1}'
        v_bottom = '{' + str(1 - p_zoom_rect[3] / 100) + r'\ht1}'

        v_trim = v_left + ' ' + v_bottom + ' ' + v_right + ' ' + v_top
        p_chapter.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + p_filename + r'"}}'))

    # Get the height of the figure
    p_chapter.append(pl.NoEscape(r'\newdimen\imageheightA'))
    p_chapter.append(pl.NoEscape(r'\settoheight{\imageheightA}{\includegraphics[width=' + p_width + r'-1em]{"' + p_filename + r'"}}'))

    # Get the height if the text
    p_chapter.append(pl.NoEscape(r'\newdimen\textheightA'))
    p_chapter.append(pl.NoEscape(r'\setbox0=\vbox{' + p_text + '}'))
    p_chapter.append(pl.NoEscape(r'\textheightA=\ht0 \advance\textheightA by \dp0'))

    p_chapter.append(pl.NoEscape(r'\makeatletter'))

    # Strip 'pt' from heights
    p_chapter.append(pl.NoEscape(r'\def\imageheightB{\strip@pt\imageheightA}'))
    p_chapter.append(pl.NoEscape(r'\def\textheightB{\strip@pt\textheightA}'))
    p_chapter.append(pl.NoEscape(r'\def\lineheight{\strip@pt\baselineskip}'))

    # Initialise variables
    p_chapter.append(pl.NoEscape(r'\def\deltaheight{0}'))
    p_chapter.append(pl.NoEscape(r'\def\remaininglines{0}'))

    # Calculate the remaining number of lines as a float
    p_chapter.append(pl.NoEscape(r'\FPsub\deltaheight\imageheightB\textheightB'))
    p_chapter.append(pl.NoEscape(r'\FPdiv\remaininglines\deltaheight\lineheight'))

    p_chapter.append(pl.NoEscape(r'\makeatother'))

    # Calculate the remaining number of lines as an integer
    p_chapter.append(pl.NoEscape(r'\setcounter{maxlines}{\intpart\remaininglines}'))
    p_chapter.append(pl.NoEscape(r'\addtocounter{maxlines}{1}'))

    # TODO: Move this to hkLatex in a pylatex format
    # Add the figure
    p_chapter.append(pl.NoEscape(r'\begin{wrapfigure}{' + p_position + '}{' + p_width + '}'))
    p_chapter.append(pl.NoEscape(r'\centering'))
    p_chapter.append(pl.NoEscape(r'\vspace{-1em}'))

    if p_zoom_rect is not None:
        p_chapter.append(pl.NoEscape(r'\includegraphics[trim=' + v_trim + ', clip, width=' + p_width + r'-1em]{"' + p_filename + r'"}'))
    else:
        p_chapter.append(pl.NoEscape(r'\includegraphics[width=' + p_width + r'-1em]{"' + p_filename + r'"}'))

    if p_caption is not None:
        p_chapter.append(pl.NoEscape(r'\caption{' + pu.escape_latex(p_caption) + r'}'))

    p_chapter.append(pl.NoEscape(r'\end{wrapfigure}'))

    # Add the text
    p_chapter.append(pl.NoEscape(p_text))

    # Add the empty lines
    p_chapter.append(pl.NoEscape(r'\setcounter{mycounter}{1}'))
    p_chapter.append(pl.NoEscape(r'\loop'))
    p_chapter.append(pl.NoEscape(r'\textcolor{white}{Empty line\\}'))
    # p_chapter.append(pl.NoEscape(r'\par'))
    p_chapter.append(pl.NoEscape(r'\addtocounter{mycounter}{1}'))
    p_chapter.append(pl.NoEscape(r'\ifnum \value{mycounter}<\value{maxlines}'))
    p_chapter.append(pl.NoEscape(r'\repeat'))
    p_chapter.append(pl.NoEscape(r'\par'))


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
        #        v_figure.show()
        v_figure.savefig(fname=v_file_path, bbox_inches='tight', pad_inches=0.0, transparent=True, dpi=500)
        plt.close(v_figure)

    return v_file_path


def get_country_min_max_coordinates(p_country_code):
    # Load list of Countries of the world from current working directory
    v_cwd = os.getcwd()
    v_file_path = os.path.join(v_cwd, 'cow.txt')
    v_data_frame = pd.read_csv(v_file_path, sep=';', comment='#')

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
    v_data_frame = pd.read_csv(v_file_path, sep=';', comment='#')

    v_data_frame = v_data_frame.loc[v_data_frame['adm0_a3'] == p_country_code, ['continent', 'subregion']]
    v_region_list = v_data_frame.values.tolist()[0]

    # Debug
    logging.debug('get_country_continent_subregion: '.join(map(str, v_region_list)))

    return v_region_list
