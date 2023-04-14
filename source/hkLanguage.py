# Dictionary of dictionaries containing string to several languages

import logging

# gLanguage = 'nl'
gStrings = {}

# Constants for chapter labels
gStrings['part'] = {'en': 'Part', 'nl': "Deel"}
gStrings['chapter'] = {'en': 'Chapter', 'nl': "Hoofdstuk"}
gStrings['table of contents'] = {'en': "Table of Contents", 'nl': "Inhoudsopgave"}
gStrings['list of figures'] = {'en': "List of Figures", 'nl': "Lijst van figuren"}

# Constant titles for parts, chapters, sections, etc.
gStrings['pedigree of'] = {'en': "Pedigree of", 'nl': "Stamboom van"}
gStrings['generation'] = {'en': "Generation", 'nl': "Generatie"}
gStrings['life sketch'] = {'en': "Life Sketch", 'nl': "Levensloop"}
gStrings['vital information'] = {'en': "Vital Information", 'nl': "Vitale informatie"}
gStrings['family'] = {'en': "Family", 'nl': "Familie"}
gStrings['parental family'] = {'en': "Parental family", 'nl': "Ouderlijk gezin"}
gStrings['family events'] = {'en': "Family events", 'nl': "Familie gebeurtenissen"}
gStrings['children'] = {'en': "Children", 'nl': "Kinderen"}
gStrings['education'] = {'en': "Education", 'nl': "Opleidingen"}
gStrings['occupation'] = {'en': "Occupation", 'nl': "Werk"}
gStrings['residences'] = {'en': "Residences", 'nl': "Verblijfplaatsen"}
gStrings['photos'] = {'en': "Photos", 'nl': "Foto's"}
gStrings['documents'] = {'en': "Documents", 'nl': "Documenten"}
gStrings['timeline'] = {'en': "Timeline", 'nl': "Tijdlijn"}

# Table fields
gStrings['call name'] = {'en': "Call name", 'nl': "Roepnaam"}
gStrings['gender'] = {'en': "Gender", 'nl': "Geslacht"}
gStrings['date of birth'] = {'en': "Date of birth", 'nl': "Geboortedatum"}
gStrings['place of birth'] = {'en': "Place of birth", 'nl': "Geboorteplaats"}
gStrings['date of baptism'] = {'en': "Date of baptism", 'nl': "Doopdatum"}
gStrings['place of baptism'] = {'en': "Place of baptism", 'nl': "Doopplaats"}
gStrings['date of christening'] = {'en': "Date of christening", 'nl': "Doopdatum"}
gStrings['place of christening'] = {'en': "Place of christening", 'nl': "Doopplaats"}
gStrings['date of adult christening'] = {'en': "Date of adult christening", 'nl': "Doopdatum"}
gStrings['place of adult christening'] = {'en': "Place of adudlt christening", 'nl': "Doopplaats"}
gStrings['date of confirmation'] = {'en': "Date of confirmation", 'nl': "Datum van het vormsel"}
gStrings['place of confirmation'] = {'en': "Place of confirmation", 'nl': "Plaats van het vormsel"}
gStrings['date of death'] = {'en': "Date of death", 'nl': "Datum van overlijden"}
gStrings['place of death'] = {'en': "Place of death", 'nl': "Plaats van overlijden"}
gStrings['date of burial'] = {'en': "Date of burial", 'nl': "Datum van begrafenis"}
gStrings['place of burial'] = {'en': "Place of burial", 'nl': "Plaats van begrafenis"}
gStrings['date of cremation'] = {'en': "Date of cremation", 'nl': "Datum van crematie"}
gStrings['place of cremation'] = {'en': "Place of cremation", 'nl': "Plaats van crematie"}
gStrings['date of engagement'] = {'en': "Date of engagement", 'nl': "Datum van verloving"}
gStrings['place of engagement'] = {'en': "Place of engagement", 'nl': "Plaats van verloving"}
gStrings['date of marriage license'] = {'en': "Date of marriage license", 'nl': "Datum van huwelijksvergunning"}
gStrings['place of marriage license'] = {'en': "Place of marriage license", 'nl': "Plaats van huwelijksvergunning"}
gStrings['date of marriage'] = {'en': "Date of marriage", 'nl': "Trouwdatum"}
gStrings['date of alternate marriage'] = {'en': "Date of alternate marriage", 'nl': "Alternatieve trouwdatum"}
gStrings['place of alternate marriage'] = {'en': "Place of alternate marriage", 'nl': "Alternatieve trouwplaats"}
gStrings['place of marriage'] = {'en': "Place of marriage", 'nl': "Trouwlokatie"}
gStrings['date of emigration'] = {'en': "Date of emigration", 'nl': "Emigratiedatum"}
gStrings['place of emigration'] = {'en': "Place of emigration", 'nl': "Emigratieplaats"}

gStrings['father'] = {'en': "Father", 'nl': "Vader"}
gStrings['mother'] = {'en': "Mother", 'nl': "Moeder"}
gStrings['self'] = {'en': "Self", 'nl': "Zelf"}
gStrings['brother'] = {'en': "Brother", 'nl': "Broer"}
gStrings['sister'] = {'en': "Sister", 'nl': "Zus"}
gStrings['son'] = {'en': "Son", 'nl': "Zoon"}
gStrings['daughter'] = {'en': "Daughter", 'nl': "Dochter"}
gStrings['male'] = {'en': "Male", 'nl': "Man"}
gStrings['female'] = {'en': "Daughter", 'nl': "Vrouw"}
gStrings['unknown'] = {'en': "Unknown", 'nl': "Onbekend"}

gStrings['date'] = {'en': "Date", 'nl': "Datum"}
gStrings['course'] = {'en': "Course", 'nl': "Opleiding"}
gStrings['profession'] = {'en': "Profession", 'nl': "Beroep"}
gStrings['residence'] = {'en': "Residence", 'nl': "Woonplaats"}

# Life Sketch
gStrings['he'] = {'en': "He", 'nl': "Hij"}
gStrings['she'] = {'en': "She", 'nl': "Zij"}
gStrings['his'] = {'en': "His", 'nl': "Zijn"}
gStrings['her'] = {'en': "Her", 'nl': "Haar"}

gStrings['{0} was born on {1}'] = {'en': "{0} was born on {1}", 'nl': "{0} is geboren op {1}"}
gStrings['{0} was born about {1}'] = {'en': "{0} was born about {1}", 'nl': "{0} is geboren omtrent {1}"}
gStrings['in {0}'] = {'en': "in {0}", 'nl': "in {0}"}

gStrings['{0} call name was {1}.'] = {'en': "{0} call name was {1}.", 'nl': "{0} roepnaam was {1}."}

gStrings['{0} had one sister:'] = {'en': "{0} had one sister", 'nl': "{0} had een zus"}
gStrings['{0} had {1} sisters:'] = {'en': "{0} had {1} sisters:", 'nl': "{0} had {1} zussen:"}
gStrings['and one brother:'] = {'en': "and one brother:", 'nl': "en een broer:"}
gStrings['and {0} brothers:'] = {'en': "and {0} brothers:", 'nl': "en {0} broers:"}
gStrings['{0} had one brother:'] = {'en': "{0} had one brother:", 'nl': "{0} had een broer:"}
gStrings['{0} had {1} brothers:'] = {'en': "{0} had {1} brothers:", 'nl': "{0} had {1} broers:"}
gStrings['{0} was {1} of'] = {'en': "{0} was {1} of", 'nl': "{0} was {1} van"}
# gStrings['and'] = {'en': "and", 'nl': "en"}
# gStrings['furthermore,'] = {'en': "furthermore,", 'nl': "daarnaast"}
# gStrings['had'] = {'en': "had", 'nl': "had"}
gStrings['{0} had one daughter:'] = {'en': "{0} had one daughter:", 'nl': "{0} had een dochter:"}
gStrings['{0} had {1} daughters:'] = {'en': "{0} had {1} daughters:", 'nl': "{0} had {1} dochters:"}
gStrings['furthermore, {0} had one daughter:'] = {'en': "furthermore, {0} had one daughter:", 'nl': "daarnaast had {0} een dochter:"}
gStrings['furthermore, {0} had {1} daughters:'] = {'en': "furthermore, {0} had {1} daughters:", 'nl': "daarnaast had {0} {1} dochters:"}
# gStrings['and one son:'] = {'en': "and one son:", 'nl': "en een zoon:"}
# gStrings['and {0} sons:'] = {'en': "and {0} sons:", 'nl': "en {0} zonen:"}
gStrings['{0} had one son:'] = {'en': "{0} had one son:", 'nl': "{0} had een zoon:"}
gStrings['{0} had {1} sons:'] = {'en': "{0} had {1} sons:", 'nl': "{0} had {1} zonen:"}
gStrings['furthermore, {0} had one son:'] = {'en': "furthermore, {0} had one son:", 'nl': "daarnaast had {0} een zoon:"}
gStrings['furthermore, {0} had {1} sons:'] = {'en': "furthermore, {0} had {1} sons:", 'nl': "daarnaast had {0} {1} zonen:"}
gStrings['{0} was {1} of'] = {'en': "{0} was {1} of", 'nl': "{0} was {1} van"}
gStrings['furthermore, {0} was {1} of'] = {'en': "furthermore, {0} was {1} of", 'nl': "daarnaast was {0} {1} van"}
# gStrings['{0} children:'] = {'en': "{0} children:", 'nl': "{0} kinderen:"}
gStrings['{0} died on {1}'] = {'en': "{0} died on {1}", 'nl': "{0} is gestorven op {1}"}
gStrings['in {0}.'] = {'en': "in {0}.", 'nl': "in {0}."}
gStrings['{0} died about {1}'] = {'en': "{0} died about {1}", 'nl': "{0} is gestorven omtrent {1}"}
gStrings['and was buried in {0}.'] = {'en': "and was buried in {0}.", 'nl': "en is begraven in {0}."}

# Months
gStrings['january'] = {'en': 'January', 'nl': 'januari'}
gStrings['february'] = {'en': 'February', 'nl': 'februari'}
gStrings['march'] = {'en': 'March', 'nl': 'maart'}
gStrings['april'] = {'en': 'April', 'nl': 'april'}
gStrings['may'] = {'en': 'May', 'nl': 'mei'}
gStrings['june'] = {'en': 'June', 'nl': 'juni'}
gStrings['july'] = {'en': 'July', 'nl': 'juli'}
gStrings['august'] = {'en': 'August', 'nl': 'augustus'}
gStrings['september'] = {'en': 'September', 'nl': 'september'}
gStrings['october'] = {'en': 'October', 'nl': 'oktober'}
gStrings['november'] = {'en': 'November', 'nl': 'november'}
gStrings['december'] = {'en': 'December', 'nl': 'december'}

gStrings['jan'] = {'en': 'Jan', 'nl': 'jan'}
gStrings['feb'] = {'en': 'Feb', 'nl': 'feb'}
gStrings['mar'] = {'en': 'Mar', 'nl': 'mrt'}
gStrings['apr'] = {'en': 'Apr', 'nl': 'apr'}
gStrings['may'] = {'en': 'May', 'nl': 'mei'}
gStrings['jun'] = {'en': 'Jun', 'nl': 'jun'}
gStrings['jul'] = {'en': 'Jul', 'nl': 'jul'}
gStrings['aug'] = {'en': 'Aug', 'nl': 'aug'}
gStrings['sep'] = {'en': 'Sep', 'nl': 'sep'}
gStrings['oct'] = {'en': 'Oct', 'nl': 'okt'}
gStrings['nov'] = {'en': 'Nov', 'nl': 'nov'}
gStrings['dec'] = {'en': 'Dec', 'nl': 'dec'}

# Date ranges
gStrings['about'] = {'en': 'about', 'nl': 'omstreeks'}
gStrings['before'] = {'en': 'before', 'nl': 'voo'}
gStrings['after'] = {'en': 'after', 'nl': 'na'}
gStrings['between'] = {'en': 'between', 'nl': 'tussen'}
gStrings['and'] = {'en': 'en', 'nl': 'en'}
gStrings['from'] = {'en': 'from', 'nl': 'van'}
gStrings['until'] = {'en': 'until', 'nl': 'tot'}

# Events
gStrings['birth'] = {'en': 'birth', 'nl': 'geboorte'}
gStrings['baptism'] = {'en': 'baptism', 'nl': 'doop'}
gStrings['christening'] = {'en': 'christening', 'nl': 'doop'}
gStrings['death'] = {'en': 'death', 'nl': 'overlijden'}
gStrings['burial'] = {'en': 'burial', 'nl': 'begravenis'}
gStrings['engagement'] = {'en': 'engagement', 'nl': 'verloving'}
gStrings['marriage'] = {'en': 'marriage', 'nl': 'huwelijk'}
gStrings['property'] = {'en': 'property', 'nl': 'eigendom'}
gStrings['graduation'] = {'en': 'graduation', 'nl': 'afstuderen'}
gStrings['retirement'] = {'en': 'retirement', 'nl': 'pensioen'}
gStrings['military service'] = {'en': 'military service', 'nl': 'militaire dienst'}
gStrings['cremation'] = {'en': 'cremation', 'nl': 'crematie'}
gStrings['medical information'] = {'en': 'medical information', 'nl': 'medische informatie'}
gStrings['census'] = {'en': 'census', 'nl': 'volkstelling'}
gStrings['confirmation'] = {'en': 'confirmation', 'nl': 'vormsel'}



def translate(p_string, p_language='nl'):
    v_return_string = ''

    if len(p_string) > 0:
        try:
            v_return_string = gStrings[p_string.strip().lower()][p_language]
        except KeyError:
            logging.warning("KEY ERROR in hkLanguage.translate: %s", p_string)

        if p_string[0].isupper():
            v_return_string = v_return_string.capitalize()

    return v_return_string
