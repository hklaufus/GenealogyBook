import hkGrampsDb as hgd
import hkLanguage as hkl

import calendar

import pylatex as pl
import pylatex.utils as pu

# https://matplotlib.org/basemap/index.html
#from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt
#import matplotlib.axes as axs
import matplotlib.figure as fig

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.mpl.geoaxes as cga

import os
import pandas as pd

from PIL import Image

def GetStartDate(pDateList, pAbbreviated=True):
    vDateString   = '-'

    if(len(pDateList)==4) or (len(pDateList)==7):
        vDay1 = pDateList[1]
        vMonth1 = pDateList[2]
        vYear1 = pDateList[3]

        vMonthString1 = calendar.month_name[vMonth1]
        if(pAbbreviated):
            vMonthString1 = calendar.month_abbr[vMonth1]

        vMonthString1 = hkl.Translate(vMonthString1)

        vDateString = ((str(vDay1) + ' ') if vDay1!=0 else '') + vMonthString1 + ' ' + str(vYear1)

    return vDateString

def DateToText(pDateList, pAbbreviated=True):
    vModifier = 0
    vModifierSet = {1, 2, 3}
    vDateString = '-'

    if(len(pDateList)==4):
        vModifier = pDateList[0]

        vDay1 = pDateList[1]
        vMonth1 = pDateList[2]
        vYear1 = pDateList[3]
        
        vMonthString1 = calendar.month_name[vMonth1]
        if(pAbbreviated):
            vMonthString1 = calendar.month_abbr[vMonth1]

        vMonthString1 = hkl.Translate(vMonthString1)

        if(vModifier in vModifierSet):
            # Before, after, about
            vDateString = hkl.Translate(hgd.vDateModifierDict[vModifier]) + ' ' + ((str(vDay1) + ' ') if vDay1!=0 else '') + vMonthString1 + ' ' + str(vYear1)
        else:
            vDateString = ((str(vDay1) + ' ') if vDay1!=0 else '') + vMonthString1 + ' ' + str(vYear1)

    elif(len(pDateList)==7):
        vModifier = pDateList[0]

        vDay1 = pDateList[1]
        vMonth1 = pDateList[2]
        vYear1 = pDateList[3]

        vMonthString1 = calendar.month_name[vMonth1]
        if(pAbbreviated):
            vMonthString1 = calendar.month_abbr[vMonth1]

        vMonthString1 = hkl.Translate(vMonthString1)

        vDay2 = pDateList[4]
        vMonth2 = pDateList[5]
        vYear2 = pDateList[6]

        vMonthString2 = calendar.month_name[vMonth2]
        if(pAbbreviated):
            vMonthString2 = calendar.month_abbr[vMonth2]

        vMonthString2 = hkl.Translate(vMonthString2)

        if(vModifier == 4):
            # Range
            vDateString = hkl.Translate('between') + ' ' + ((str(vDay1) + ' ') if vDay1!=0 else '') + vMonthString1 + ' ' + str(vYear1) + ' ' + hkl.Translate('and') + ' ' + ((str(vDay2) + ' ') if vDay2!=0 else '') + vMonthString2 + ' ' + str(vYear2)
        elif(vModifier == 5):
            # Span
            vDateString = hkl.Translate('from') + ' ' + ((str(vDay1) + ' ') if vDay1!=0 else '') + vMonthString1 + ' ' + str(vYear1) + ' ' + hkl.Translate('until') + ' ' + ((str(vDay2) + ' ') if vDay2!=0 else '') + vMonthString2 + ' ' + str(vYear2)

    return vDateString

def StreetToText(pPlaceList, pLongStyle=False):
    vStreetLabel      = hgd.vPlaceTypeDict[hgd.vPlaceTypeStreet]

    vString = ''
    if(pLongStyle):
        for vPlace in pPlaceList:
            vString = vString + ', ' + pPlaceList[vPlace][0]

        vString = vString[2:].strip()
    else:
        if(vStreetLabel in pPlaceList):
            vString = vString + pPlaceList[vStreetLabel][0]

            vPlaceString = PlaceToText(pPlaceList, pLongStyle)
            if(len(vPlaceString)>0):
                vString = vString + ', ' + vPlaceString
        else:
            vString = vString + PlaceToText(pPlaceList, pLongStyle)

    # Debug
#    print('pPlaceList: ', pPlaceList)
#    print('PlaceToText: ', vString)

    return vString

def PlaceToText(pPlaceList, pLongStyle=False):
    vCityLabel         = hgd.vPlaceTypeDict[hgd.vPlaceTypeCity]
    vTownLabel         = hgd.vPlaceTypeDict[hgd.vPlaceTypeTown]
    vVillageLabel      = hgd.vPlaceTypeDict[hgd.vPlaceTypeVillage]
    vMunicipalityLabel = hgd.vPlaceTypeDict[hgd.vPlaceTypeMunicipality] 

    vString = ''
    if(pLongStyle):
        for vPlace in pPlaceList:
            vString = vString + ', ' + pPlaceList[vPlace][0]

        vString = vString[2:].strip()
    else:
        vFound = True
        if(vCityLabel in pPlaceList):
            vString = vString + pPlaceList[vCityLabel][0]
        elif(vTownLabel in pPlaceList):
            vString = vString + pPlaceList[vTownLabel][0]
        elif(vVillageLabel in pPlaceList):
            vString = vString + pPlaceList[vVillageLabel][0]
        elif(vMunicipalityLabel in pPlaceList):
            vString = vString + pPlaceList[vMunicipalityLabel][0]
        else:
            vFound = False

        if(vFound):
            vCountryString = CountryToText(pPlaceList, pLongStyle)
            if(len(vCountryString)>0):
                vString = vString + ', ' + vCountryString
        else:
            vString = vString + CountryToText(pPlaceList, pLongStyle)

    # Debug
#    print('pPlaceList: ', pPlaceList)
#    print('PlaceToText: ', vString)

    return vString

def CountryToText(pPlaceList, pLongStyle=False):
    vCountryLabel      = hgd.vPlaceTypeDict[hgd.vPlaceTypeCountry]

    vString = ''
    if(pLongStyle):
        for vPlace in pPlaceList:
            vString = vString + ', ' + pPlaceList[vPlace][0]

        vString = vString[2:].strip()
    else:
        if(vCountryLabel in pPlaceList):
            vString = vString + pPlaceList[vCountryLabel][0]

    # Debug
#    print('pPlaceList: ', pPlaceList)
#    print('CountryToText: ', vString)

    return vString

def SortPersonListByBirth(pPersonHandleList, pCursor):
    # Sort ID of persons in pPersonIdList by birth date

    # Debug
#    print('Before: ',pPersonHandleList)
    
    # Retrieve person info
    vNewPersonList = []
    for vPersonHandle in pPersonHandleList:
        vPersonData = hgd.DecodePersonData(vPersonHandle, pCursor)
        vBirthRefIndex = vPersonData[6]
        if(vBirthRefIndex>=0):
            vEventRefList = vPersonData[7]
            vBirthEventRef = vEventRefList[vBirthRefIndex]
            vBirthEventHandle = vBirthEventRef[3]
            vBirthEventInfo = hgd.DecodeEventData(vBirthEventHandle, pCursor)
            vBirthDate = vBirthEventInfo[1]
        else:
            vBirthDate = '-'

        vNewPersonList.append([vBirthDate,vPersonHandle])

    vDateFunc = lambda x: "{0:0>4}{1:0>2}{2:0>2}".format(x[0][3], x[0][2], x[0][1]) if (x[0] != '-') else '-'
    vNewPersonList.sort(key=vDateFunc)
    pPersonHandleList = [item[1] for item in vNewPersonList]

    # Debug
#    print('After: ',pPersonHandleList)

    return pPersonHandleList

def PictureSideBySideEqualHeight(pChapter, pImagePath_1, pImagePath_2, pImageTitle_1 = "", pImageTitle_2 = "", pImageRect_1 = None, pImageRect_2 = None):
    """
    Positions two pictures side by side, scaling them such that thier heights are equal.
    Zoom in on a focus area in case pImageRect_# is defined
    """

    if(pImageRect_1 is None):
        pChapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[scale=0.1]{"' + pImagePath_1 + r'"}}')) # Added scale to prevent overflow in scalerel package
    else:
        vLeft_1   = '{' + str(pImageRect_1[0]/100) + '\wd1}'
        vRight_1  = '{' + str(1-pImageRect_1[2]/100) + '\wd1}'
        vTop_1    = '{' + str(pImageRect_1[1]/100) + '\ht1}'
        vBottom_1 = '{' + str(1-pImageRect_1[3]/100) + '\ht1}'

        # Debug
        #print('PictureSideBySideEqualHeight:', pImageRect_1, vLeft_1, vTop_1, vRight_1, vBottom_1)

        pChapter.append(pl.NoEscape(r'\sbox1{\includegraphics{"' + pImagePath_1 + r'"}}'))
        pChapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[trim=' + vLeft_1 + ' ' + vBottom_1 + ' ' + vRight_1 + ' ' + vTop_1 + ', clip, scale=0.1]{"' + pImagePath_1 + r'"}}'))

    if(pImageRect_2 is None):
        pChapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + pImagePath_2 + r'"}}')) # Added scale to prevent overflow in scalerel package
    else:
        vLeft_2   = '{' + str(pImageRect_2[0]/100) + '\wd2}'
        vRight_2  = '{' + str(1-pImageRect_2[2]/100) + '\wd2}'
        vTop_2    = '{' + str(pImageRect_2[1]/100) + '\ht2}'
        vBottom_2 = '{' + str(1-pImageRect_2[3]/100) + '\ht2}'

        pChapter.append(pl.NoEscape(r'\sbox2{\includegraphics{"' + pImagePath_2 + r'"}}'))
        pChapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[trim=' + vLeft_2 + ' ' + vBottom_2 + ' ' + vRight_2 + ' ' + vTop_2 + ', clip, scale=0.1]{"' + pImagePath_2 + r'"}}'))

    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

    pChapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))
    pChapter.append(pl.NoEscape(r'\imgwidthA=\wd\x'))
    pChapter.append(pl.NoEscape(r'\textwidthA=\dimexpr\textwidth-5ex'))
    pChapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\textwidthA}{\the\imgwidthA}'))
    pChapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))
    pChapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    pChapter.append(pl.NoEscape(r'\box0'))
    pChapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageTitle_1) + '}'))
    pChapter.append(pl.NoEscape(r'\end{minipage}\kern3ex'))
    pChapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
    pChapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    pChapter.append(pl.NoEscape(r'\box0'))
    pChapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageTitle_2) + '}'))
    pChapter.append(pl.NoEscape(r'\end{minipage}'))
    pChapter.append(pl.NoEscape(r'\newline\newline'))

def PictureSideBySideEqualHeight_Old(pChapter, pImageData_1, pImageData_2):
    # See: https://tex.stackexchange.com/questions/244635/side-by-side-figures-adjusted-to-have-equal-height

    pChapter.append(pl.NoEscape(r'\def\imgA{\includegraphics[scale=0.1]{"' + pImageData_1[2] + r'"}}'))  # Added scale to prevent overflow in scalerel package
    pChapter.append(pl.NoEscape(r'\def\imgB{\includegraphics[scale=0.1]{"' + pImageData_2[2] + r'"}}'))
    pChapter.append(pl.NoEscape(r'\sbox\x{\scalerel{$\imgA$}{$\imgB$}}'))
    pChapter.append(pl.NoEscape(r'\imgwidthA=\wd\x'))
    pChapter.append(pl.NoEscape(r'\textwidthA=\dimexpr\textwidth-5ex'))
    pChapter.append(pl.NoEscape(r'\FPdiv\scaleratio{\the\textwidthA}{\the\imgwidthA}'))
    pChapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\scalerel*{$\imgA$}{$\imgB$}}}'))
    pChapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    pChapter.append(pl.NoEscape(r'\box0'))
    pChapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageData_1[4]) + '}'))
    pChapter.append(pl.NoEscape(r'\end{minipage}\kern3ex'))
    pChapter.append(pl.NoEscape(r'\setbox0=\hbox{\scalebox{\scaleratio}{\imgB}}'))
    pChapter.append(pl.NoEscape(r'\begin{minipage}[t]{\wd0}'))
    pChapter.append(pl.NoEscape(r'\box0'))
    pChapter.append(pl.NoEscape(r'\captionof{figure}{' + pu.escape_latex(pImageData_2[4]) + '}'))
    pChapter.append(pl.NoEscape(r'\end{minipage}'))
    pChapter.append(pl.NoEscape(r'\newline\newline'))

def WrapFigure(pChapter, pFilename, pCaption=None, pPosition='i', pWidth=r'0.50\textwidth', pText=''):
    # This is a very ugly function, but what it does:
    # 1. It simplifies the use of the wrapfigure environment
    # 2. It fills the textblock with empty line in case the figure height is longer then the text block height.
    # This happens when the text block contains too little text lines, with the result that the next section heading and following text would overlap the figure

    # Get the height of the figure
    pChapter.append(pl.NoEscape(r'\newdimen\imageheightA'))
    pChapter.append(pl.NoEscape(r'\settoheight{\imageheightA}{\includegraphics[width='+pWidth+r'-1em]{"' + pFilename + r'"}}'))

    # Get the height if the text
    pChapter.append(pl.NoEscape(r'\newdimen\textheightA'))
    pChapter.append(pl.NoEscape(r'\setbox0=\vbox{' + pText  + '}'))
    pChapter.append(pl.NoEscape(r'\textheightA=\ht0 \advance\textheightA by \dp0'))

    pChapter.append(pl.NoEscape(r'\makeatletter'))

    # Strip 'pt' from heights
    pChapter.append(pl.NoEscape(r'\def\imageheightB{\strip@pt\imageheightA}'))
    pChapter.append(pl.NoEscape(r'\def\textheightB{\strip@pt\textheightA}'))
    pChapter.append(pl.NoEscape(r'\def\lineheight{\strip@pt\baselineskip}'))

    # Initialise variables
    pChapter.append(pl.NoEscape(r'\def\deltaheight{0}'))
    pChapter.append(pl.NoEscape(r'\def\remaininglines{0}'))

    # Calculate the remaining number of lines as a float
    pChapter.append(pl.NoEscape(r'\FPsub\deltaheight\imageheightB\textheightB'))
    pChapter.append(pl.NoEscape(r'\FPdiv\remaininglines\deltaheight\lineheight'))

    pChapter.append(pl.NoEscape(r'\makeatother'))

    # Calculate the remaining number of lines as an integer
    pChapter.append(pl.NoEscape(r'\setcounter{maxlines}{\intpart\remaininglines}'))
    pChapter.append(pl.NoEscape(r'\addtocounter{maxlines}{1}'))

    # TODO: Move this to hkLatex in a pylatex format
    # Add the figure
    pChapter.append(pl.NoEscape(r'\begin{wrapfigure}{'+pPosition+'}{'+pWidth+'}'))
    pChapter.append(pl.NoEscape(r'\centering'))
    pChapter.append(pl.NoEscape(r'\vspace{-1em}'))
    pChapter.append(pl.NoEscape(r'\includegraphics[width='+pWidth+r'-1em]{"' + pFilename + r'"}'))

    if(pCaption is not None):
        pChapter.append(pl.NoEscape(r'\caption{' + pu.escape_latex(pCaption) + r'}'))

    pChapter.append(pl.NoEscape(r'\end{wrapfigure}'))

    # Add the text
    pChapter.append(pl.NoEscape(pText))

    # Add the empty lines
    pChapter.append(pl.NoEscape(r'\setcounter{mycounter}{1}'))
    pChapter.append(pl.NoEscape(r'\loop'))
    pChapter.append(pl.NoEscape(r'\textcolor{white}{Empty line\\}'))
    #pChapter.append(pl.NoEscape(r'\par'))
    pChapter.append(pl.NoEscape(r'\addtocounter{mycounter}{1}'))
    pChapter.append(pl.NoEscape(r'\ifnum \value{mycounter}<\value{maxlines}'))
    pChapter.append(pl.NoEscape(r'\repeat'))

def CreateMap(pDocumentPath, pCountry):
    # Check for existence of path
    if(not os.path.exists(pDocumentPath)):
        os.mkdir(pDocumentPath)

    # Create file name for figure
    vFilePath = os.path.join(pDocumentPath, 'Map_' + pCountry + '.png')
    if(not os.path.exists(vFilePath)):
        # Get country latitude / longitudes
        vCoordinates = GetCountryMinMaxCoordinates(pCountry)
        vLon0 = vCoordinates[0]
        vLat0 = vCoordinates[1]
        vLon1 = vCoordinates[2]
        vLat1 = vCoordinates[3]

        # Draw map
#        vFigure = fig.Figure()
#        vAxes = cga.GeoAxes(rect=[0, 1, 0, 1], fig=vFigure, map_projection=ccrs.Mercator())
        vAxes = plt.axes(projection=ccrs.Mercator())
        vAxes.set_extent([vLon0, vLon1, vLat0, vLat1])
        vAxes.add_feature(cfeature.LAND.with_scale('10m')) #, color='Bisque')
        vAxes.add_feature(cfeature.LAKES.with_scale('10m'), alpha=0.5)
        vAxes.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.2)
        vAxes.add_feature(cfeature.OCEAN.with_scale('10m'), linewidth=0.2)

        vFigure = vAxes.get_figure()
#        vFigure.show()
        vFigure.savefig(fname=vFilePath, bbox_inches='tight', pad_inches=0.0, transparent=True, dpi=500)
        plt.close(vFigure)

    return vFilePath

def GetCountryMinMaxCoordinates(pCountryCode):
    # Load list of Countries of the world from current working directory
    vCwd = os.getcwd()
    vFilePath = os.path.join(vCwd, 'cow.txt')
    vDataFrame = pd.read_csv(vFilePath, sep=';', comment='#')

    # 20220109: Limit number of maps to Netherlands, Western Europe and the World
    if(pCountryCode == 'WEU'):
        # Western Europe
        vDataFrame = vDataFrame.loc[vDataFrame['subregion']=='Western Europe', ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        vMinMaxList = [vDataFrame['min_lon'].min(), vDataFrame['min_lat'].min(), vDataFrame['max_lon'].max(), vDataFrame['max_lat'].max()]
    elif(pCountryCode == 'EUR'):
        # Western Europe
        vDataFrame = vDataFrame.loc[vDataFrame['continent']=='Europe', ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        vMinMaxList = [vDataFrame['min_lon'].min(), vDataFrame['min_lat'].min(), vDataFrame['max_lon'].max(), vDataFrame['max_lat'].max()]
    elif(pCountryCode == 'WLD'):
        # World
        vMinMaxList = [-179.,-89.,179.,89.]
    else:
        vDataFrame = vDataFrame.loc[vDataFrame['adm0_a3']==pCountryCode, ['min_lon', 'min_lat', 'max_lon', 'max_lat']]
        vMinMaxList = vDataFrame.values.tolist()[0]
        
    # Debug
#    print('GetCountryMinMaxCoordinates: ', vMinMaxList)

    return vMinMaxList

def GetCountryContinentSubregion(pCountryCode):
    # Load list of Countries of the world from current working directory
    vCwd = os.getcwd()
    vFilePath = os.path.join(vCwd, 'cow.txt')
    vDataFrame = pd.read_csv(vFilePath, sep=';', comment='#')

    vDataFrame = vDataFrame.loc[vDataFrame['adm0_a3']==pCountryCode, ['continent', 'subregion']]
    vRegionList = vDataFrame.values.tolist()[0]
        
    # Debug
#    print('GetCountryContinentSubregion: ', vRegionList)

    return vRegionList

