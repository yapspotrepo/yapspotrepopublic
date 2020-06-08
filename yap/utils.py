from django.utils.translation import ugettext_lazy as _
import string 
import bleach
import pytz
from django.urls import reverse
from django.core.mail import EmailMessage
from allauth.account.admin import EmailAddress


#ASCII_ALPHANUMERIC = string.ascii_letters + string.digits 
ASCII_NUMERIC = string.digits 


GENDER_CHOICES = (
    ("",  _('Not Specified')),
    ('M', _('Male')),
    ('F', _('Female')),
    ('O', _('Other')),  ### It's 2020. lol.
)


ACTIVITY_CATEGORIES = [
    ("", "-----"),
    ("art", "Arts"),
    ("book", "Book Clubs"),
    ("biz", "Business and Career"),
    ("fash", "Fashion and Beauty"),
    ("film", "Film"),
    ("fit", "Fitness"),
    ("game", "Games"),
    ("hobb", "Hobbies"),
    ("lang", "Languages"),
    ("yoga", "Meditation and Yoga"),
    ("meet", "Meeting New People"),
    ("mus", "Music"),
    ("pet", "Pets"),
    ("photo", "Photography"),
    ("polit", "Politics"),
    ("speak", "Public Speaking"),
    ("relig", "Religion"),
    ("soc", "Socializing"),
    ("sport", "Sports"),
    ("tech", "Technology"),
    ("other", "Other"),
]


COUNTRY_CHOICES = [
    ("", "-----"),
    ('AW', 'Aruba'),
    ('AF', 'Afghanistan'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AX', 'Åland Islands'),
    ('AL', 'Albania'),
    ('AD', 'Andorra'),
    ('AE', 'United Arab Emirates'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AS', 'American Samoa'),
    ('AQ', 'Antarctica'),
    ('TF', 'French Southern Territories'),
    ('AG', 'Antigua and Barbuda'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BI', 'Burundi'),
    ('BE', 'Belgium'),
    ('BJ', 'Benin'),
    ('BQ', 'Bonaire, Sint Eustatius and Saba'),
    ('BF', 'Burkina Faso'),
    ('BD', 'Bangladesh'),
    ('BG', 'Bulgaria'),
    ('BH', 'Bahrain'),
    ('BS', 'Bahamas'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BL', 'Saint Barthélemy'),
    ('BY', 'Belarus'),
    ('BZ', 'Belize'),
    ('BM', 'Bermuda'),
    ('BO', 'Bolivia'),
    ('BR', 'Brazil'),
    ('BB', 'Barbados'),
    ('BN', 'Brunei Darussalam'),
    ('BT', 'Bhutan'),
    ('BV', 'Bouvet Island'),
    ('BW', 'Botswana'),
    ('CF', 'Central African Republic'),
    ('CA', 'Canada'),
    ('CC', 'Cocos (Keeling) Islands'),
    ('CH', 'Switzerland'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CI', "Côte d'Ivoire"),
    ('CM', 'Cameroon'),
    ('CD', 'Congo, The Democratic Republic of the'),
    ('CG', 'Congo'),
    ('CK', 'Cook Islands'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CV', 'Cabo Verde'),
    ('CR', 'Costa Rica'),
    ('CU', 'Cuba'),
    ('CW', 'Curaçao'),
    ('CX', 'Christmas Island'),
    ('KY', 'Cayman Islands'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czechia'),
    ('DE', 'Germany'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DK', 'Denmark'),
    ('DO', 'Dominican Republic'),
    ('DZ', 'Algeria'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('ER', 'Eritrea'),
    ('EH', 'Western Sahara'),
    ('ES', 'Spain'),
    ('EE', 'Estonia'),
    ('ET', 'Ethiopia'),
    ('FI', 'Finland'),
    ('FJ', 'Fiji'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FR', 'France'),
    ('FO', 'Faroe Islands'),
    ('FM', 'Micronesia, Federated States of'),
    ('GA', 'Gabon'),
    ('GB', 'United Kingdom'),
    ('GE', 'Georgia'),
    ('GG', 'Guernsey'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GN', 'Guinea'),
    ('GP', 'Guadeloupe'),
    ('GM', 'Gambia'),
    ('GW', 'Guinea-Bissau'),
    ('GQ', 'Equatorial Guinea'),
    ('GR', 'Greece'),
    ('GD', 'Grenada'),
    ('GL', 'Greenland'),
    ('GT', 'Guatemala'),
    ('GF', 'French Guiana'),
    ('GU', 'Guam'),
    ('GY', 'Guyana'),
    ('HK', 'Hong Kong'),
    ('HM', 'Heard Island and McDonald Islands'),
    ('HN', 'Honduras'),
    ('HR', 'Croatia'),
    ('HT', 'Haiti'),
    ('HU', 'Hungary'),
    ('ID', 'Indonesia'),
    ('IM', 'Isle of Man'),
    ('IN', 'India'),
    ('IO', 'British Indian Ocean Territory'),
    ('IE', 'Ireland'),
    ('IR', 'Iran, Islamic Republic of'),
    ('IQ', 'Iraq'),
    ('IS', 'Iceland'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JE', 'Jersey'),
    ('JO', 'Jordan'),
    ('JP', 'Japan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KG', 'Kyrgyzstan'),
    ('KH', 'Cambodia'),
    ('KI', 'Kiribati'),
    ('KN', 'Saint Kitts and Nevis'),
    ('KR', 'Korea, Republic of'),
    ('KW', 'Kuwait'),
    ('LA', "Lao People's Democratic Republic"),
    ('LB', 'Lebanon'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LC', 'Saint Lucia'),
    ('LI', 'Liechtenstein'),
    ('LK', 'Sri Lanka'),
    ('LS', 'Lesotho'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('LV', 'Latvia'),
    ('MO', 'Macao'),
    ('MF', 'Saint Martin (French part)'),
    ('MA', 'Morocco'),
    ('MC', 'Monaco'),
    ('MD', 'Moldova'),
    ('MG', 'Madagascar'),
    ('MV', 'Maldives'),
    ('MX', 'Mexico'),
    ('MH', 'Marshall Islands'),
    ('MK', 'North Macedonia'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MM', 'Myanmar'),
    ('ME', 'Montenegro'),
    ('MN', 'Mongolia'),
    ('MP', 'Northern Mariana Islands'),
    ('MZ', 'Mozambique'),
    ('MR', 'Mauritania'),
    ('MS', 'Montserrat'),
    ('MQ', 'Martinique'),
    ('MU', 'Mauritius'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('YT', 'Mayotte'),
    ('NA', 'Namibia'),
    ('NC', 'New Caledonia'),
    ('NE', 'Niger'),
    ('NF', 'Norfolk Island'),
    ('NG', 'Nigeria'),
    ('NI', 'Nicaragua'),
    ('NU', 'Niue'),
    ('NL', 'Netherlands'),
    ('NO', 'Norway'),
    ('NP', 'Nepal'),
    ('NR', 'Nauru'),
    ('NZ', 'New Zealand'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PA', 'Panama'),
    ('PN', 'Pitcairn'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PW', 'Palau'),
    ('PG', 'Papua New Guinea'),
    ('PL', 'Poland'),
    ('PR', 'Puerto Rico'),
    ('KP', "Korea, Democratic People's Republic of"),
    ('PT', 'Portugal'),
    ('PY', 'Paraguay'),
    ('PS', 'Palestine, State of'),
    ('PF', 'French Polynesia'),
    ('QA', 'Qatar'),
    ('RE', 'Réunion'),
    ('RO', 'Romania'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('SA', 'Saudi Arabia'),
    ('SD', 'Sudan'),
    ('SN', 'Senegal'),
    ('SG', 'Singapore'),
    ('GS', 'South Georgia and the South Sandwich Islands'),
    ('SH', 'Saint Helena, Ascension and Tristan da Cunha'),
    ('SJ', 'Svalbard and Jan Mayen'),
    ('SB', 'Solomon Islands'),
    ('SL', 'Sierra Leone'),
    ('SV', 'El Salvador'),
    ('SM', 'San Marino'),
    ('SO', 'Somalia'),
    ('PM', 'Saint Pierre and Miquelon'),
    ('RS', 'Serbia'),
    ('SS', 'South Sudan'),
    ('ST', 'Sao Tome and Principe'),
    ('SR', 'Suriname'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SE', 'Sweden'),
    ('SZ', 'Eswatini'),
    ('SX', 'Sint Maarten (Dutch part)'),
    ('SC', 'Seychelles'),
    ('SY', 'Syrian Arab Republic'),
    ('TC', 'Turks and Caicos Islands'),
    ('TD', 'Chad'),
    ('TG', 'Togo'),
    ('TH', 'Thailand'),
    ('TJ', 'Tajikistan'),
    ('TK', 'Tokelau'),
    ('TM', 'Turkmenistan'),
    ('TL', 'Timor-Leste'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad and Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TV', 'Tuvalu'),
    ('TW', 'Taiwan'),
    ('TZ', 'Tanzania'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('UM', 'United States Minor Outlying Islands'),
    ('UY', 'Uruguay'),
    ('US', 'United States'),
    ('UZ', 'Uzbekistan'),
    ('VA', 'Holy See (Vatican City State)'),
    ('VC', 'Saint Vincent and the Grenadines'),
    ('VE', 'Venezuela'),
    ('VG', 'Virgin Islands, British'),
    ('VI', 'Virgin Islands, U.S.'),
    ('VN', 'Vietnam'),
    ('VU', 'Vanuatu'),
    ('WF', 'Wallis and Futuna'),
    ('WS', 'Samoa'),
    ('YE', 'Yemen'),
    ('ZA', 'South Africa'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe')
]


COUNTRY_CHOICES_DICT = dict(COUNTRY_CHOICES)



LANGUAGE_CHOICES = [
    ("", "-----"),
    ('ab', 'Abkhaz'),
    ('aa', 'Afar'),
    ('af', 'Afrikaans'),
    ('ak', 'Akan'),
    ('sq', 'Albanian'),
    ('am', 'Amharic'),
    ('ar', 'Arabic'),
    ('an', 'Aragonese'),
    ('hy', 'Armenian'),
    ('as', 'Assamese'),
    ('av', 'Avaric'),
    ('ae', 'Avestan'),
    ('ay', 'Aymara'),
    ('az', 'Azerbaijani'),
    ('bm', 'Bambara'),
    ('ba', 'Bashkir'),
    ('eu', 'Basque'),
    ('be', 'Belarusian'),
    ('bn', 'Bengali'),
    ('bh', 'Bihari'),
    ('bi', 'Bislama'),
    ('bs', 'Bosnian'),
    ('br', 'Breton'),
    ('bg', 'Bulgarian'),
    ('my', 'Burmese'),
    ('ca', 'Catalan; Valencian'),
    ('ch', 'Chamorro'),
    ('ce', 'Chechen'),
    ('ny', 'Chichewa; Chewa; Nyanja'),
    ('zh', 'Chinese'),
    ('cv', 'Chuvash'),
    ('kw', 'Cornish'),
    ('co', 'Corsican'),
    ('cr', 'Cree'),
    ('hr', 'Croatian'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('dv', 'Divehi; Dhivehi; Maldivian;'),
    ('nl', 'Dutch'),
    ('en', 'English'),
    ('eo', 'Esperanto'),
    ('et', 'Estonian'),
    ('ee', 'Ewe'),
    ('fo', 'Faroese'),
    ('fj', 'Fijian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('ff', 'Fula; Fulah; Pulaar; Pular'),
    ('gl', 'Galician'),
    ('ka', 'Georgian'),
    ('de', 'German'),
    ('el', 'Greek, Modern'),
    ('gn', 'Guaraní'),
    ('gu', 'Gujarati'),
    ('ht', 'Haitian; Haitian Creole'),
    ('ha', 'Hausa'),
    ('he', 'Hebrew'),
    ('iw', 'Hebrew'),
    ('hz', 'Herero'),
    ('hi', 'Hindi'),
    ('ho', 'Hiri Motu'),
    ('hu', 'Hungarian'),
    ('ia', 'Interlingua'),
    ('id', 'Indonesian'),
    ('ie', 'Interlingue'),
    ('ga', 'Irish'),
    ('ig', 'Igbo'),
    ('ik', 'Inupiaq'),
    ('io', 'Ido'),
    ('is', 'Icelandic'),
    ('it', 'Italian'),
    ('iu', 'Inuktitut'),
    ('ja', 'Japanese'),
    ('jv', 'Javanese'),
    ('kl', 'Kalaallisut, Greenlandic'),
    ('kn', 'Kannada'),
    ('kr', 'Kanuri'),
    ('ks', 'Kashmiri'),
    ('kk', 'Kazakh'),
    ('km', 'Khmer'),
    ('ki', 'Kikuyu, Gikuyu'),
    ('rw', 'Kinyarwanda'),
    ('ky', 'Kirghiz, Kyrgyz'),
    ('kv', 'Komi'),
    ('kg', 'Kongo'),
    ('ko', 'Korean'),
    ('ku', 'Kurdish'),
    ('kj', 'Kwanyama, Kuanyama'),
    ('la', 'Latin'),
    ('lb', 'Luxembourgish'),
    ('lg', 'Luganda'),
    ('li', 'Limburgish'),
    ('ln', 'Lingala'),
    ('lo', 'Lao'),
    ('lt', 'Lithuanian'),
    ('lu', 'Luba-Katanga'),
    ('lv', 'Latvian'),
    ('gv', 'Manx'),
    ('mk', 'Macedonian'),
    ('mg', 'Malagasy'),
    ('ms', 'Malay'),
    ('ml', 'Malayalam'),
    ('mt', 'Maltese'),
    ('mi', 'Māori'),
    ('mr', 'Marathi (Marāṭhī)'),
    ('mh', 'Marshallese'),
    ('mn', 'Mongolian'),
    ('na', 'Nauru'),
    ('nv', 'Navajo, Navaho'),
    ('nb', 'Norwegian Bokmål'),
    ('nd', 'North Ndebele'),
    ('ne', 'Nepali'),
    ('ng', 'Ndonga'),
    ('nn', 'Norwegian Nynorsk'),
    ('no', 'Norwegian'),
    ('ii', 'Nuosu'),
    ('nr', 'South Ndebele'),
    ('oc', 'Occitan'),
    ('oj', 'Ojibwe, Ojibwa'),
    ('om', 'Oromo'),
    ('or', 'Oriya'),
    ('os', 'Ossetian, Ossetic'),
    ('pa', 'Panjabi, Punjabi'),
    ('pi', 'Pāli'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('ps', 'Pashto, Pushto'),
    ('pt', 'Portuguese'),
    ('qu', 'Quechua'),
    ('rm', 'Romansh'),
    ('rn', 'Kirundi'),
    ('ro', 'Romanian, Moldavian, Moldovan'),
    ('ru', 'Russian'),
    ('sa', 'Sanskrit (Saṁskṛta)'),
    ('sc', 'Sardinian'),
    ('sd', 'Sindhi'),
    ('se', 'Northern Sami'),
    ('sm', 'Samoan'),
    ('sg', 'Sango'),
    ('sr', 'Serbian'),
    ('gd', 'Scottish Gaelic; Gaelic'),
    ('sn', 'Shona'),
    ('si', 'Sinhala, Sinhalese'),
    ('sk', 'Slovak'),
    ('sl', 'Slovene'),
    ('so', 'Somali'),
    ('st', 'Southern Sotho'),
    ('es', 'Spanish; Castilian'),
    ('su', 'Sundanese'),
    ('sw', 'Swahili'),
    ('ss', 'Swati'),
    ('sv', 'Swedish'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('tg', 'Tajik'),
    ('th', 'Thai'),
    ('ti', 'Tigrinya'),
    ('bo', 'Tibetan Standard, Tibetan, Central'),
    ('tk', 'Turkmen'),
    ('tl', 'Tagalog'),
    ('tn', 'Tswana'),
    ('to', 'Tonga (Tonga Islands)'),
    ('tr', 'Turkish'),
    ('ts', 'Tsonga'),
    ('tt', 'Tatar'),
    ('tw', 'Twi'),
    ('ty', 'Tahitian'),
    ('ug', 'Uighur, Uyghur'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('uz', 'Uzbek'),
    ('ve', 'Venda'),
    ('vi', 'Vietnamese'),
    ('vo', 'Volapük'),
    ('wa', 'Walloon'),
    ('cy', 'Welsh'),
    ('wo', 'Wolof'),
    ('fy', 'Western Frisian'),
    ('xh', 'Xhosa'),
    ('yi', 'Yiddish'),
    ('yo', 'Yoruba'),
    ('za', 'Zhuang, Chuang')
]

TIMEZONE_CHOICES = [
    ('Africa/Abidjan', 'Africa/Abidjan'),
    ('Africa/Accra', 'Africa/Accra'),
    ('Africa/Addis_Ababa', 'Africa/Addis_Ababa'),
    ('Africa/Algiers', 'Africa/Algiers'),
    ('Africa/Asmara', 'Africa/Asmara'),
    ('Africa/Bamako', 'Africa/Bamako'),
    ('Africa/Bangui', 'Africa/Bangui'),
    ('Africa/Banjul', 'Africa/Banjul'),
    ('Africa/Bissau', 'Africa/Bissau'),
    ('Africa/Blantyre', 'Africa/Blantyre'),
    ('Africa/Brazzaville', 'Africa/Brazzaville'),
    ('Africa/Bujumbura', 'Africa/Bujumbura'),
    ('Africa/Cairo', 'Africa/Cairo'),
    ('Africa/Casablanca', 'Africa/Casablanca'),
    ('Africa/Ceuta', 'Africa/Ceuta'),
    ('Africa/Conakry', 'Africa/Conakry'),
    ('Africa/Dakar', 'Africa/Dakar'),
    ('Africa/Dar_es_Salaam', 'Africa/Dar_es_Salaam'),
    ('Africa/Djibouti', 'Africa/Djibouti'),
    ('Africa/Douala', 'Africa/Douala'),
    ('Africa/El_Aaiun', 'Africa/El_Aaiun'),
    ('Africa/Freetown', 'Africa/Freetown'),
    ('Africa/Gaborone', 'Africa/Gaborone'),
    ('Africa/Harare', 'Africa/Harare'),
    ('Africa/Johannesburg', 'Africa/Johannesburg'),
    ('Africa/Juba', 'Africa/Juba'),
    ('Africa/Kampala', 'Africa/Kampala'),
    ('Africa/Khartoum', 'Africa/Khartoum'),
    ('Africa/Kigali', 'Africa/Kigali'),
    ('Africa/Kinshasa', 'Africa/Kinshasa'),
    ('Africa/Lagos', 'Africa/Lagos'),
    ('Africa/Libreville', 'Africa/Libreville'),
    ('Africa/Lome', 'Africa/Lome'),
    ('Africa/Luanda', 'Africa/Luanda'),
    ('Africa/Lubumbashi', 'Africa/Lubumbashi'),
    ('Africa/Lusaka', 'Africa/Lusaka'),
    ('Africa/Malabo', 'Africa/Malabo'),
    ('Africa/Maputo', 'Africa/Maputo'),
    ('Africa/Maseru', 'Africa/Maseru'),
    ('Africa/Mbabane', 'Africa/Mbabane'),
    ('Africa/Mogadishu', 'Africa/Mogadishu'),
    ('Africa/Monrovia', 'Africa/Monrovia'),
    ('Africa/Nairobi', 'Africa/Nairobi'),
    ('Africa/Ndjamena', 'Africa/Ndjamena'),
    ('Africa/Niamey', 'Africa/Niamey'),
    ('Africa/Nouakchott', 'Africa/Nouakchott'),
    ('Africa/Ouagadougou', 'Africa/Ouagadougou'),
    ('Africa/Porto-Novo', 'Africa/Porto-Novo'),
    ('Africa/Sao_Tome', 'Africa/Sao_Tome'),
    ('Africa/Tripoli', 'Africa/Tripoli'),
    ('Africa/Tunis', 'Africa/Tunis'),
    ('Africa/Windhoek', 'Africa/Windhoek'),
    ('America/Adak', 'America/Adak'),
    ('America/Anchorage', 'America/Anchorage'),
    ('America/Anguilla', 'America/Anguilla'),
    ('America/Antigua', 'America/Antigua'),
    ('America/Araguaina', 'America/Araguaina'),
    ('America/Argentina/Buenos_Aires', 'America/Argentina/Buenos_Aires'),
    ('America/Argentina/Catamarca', 'America/Argentina/Catamarca'),
    ('America/Argentina/Cordoba', 'America/Argentina/Cordoba'),
    ('America/Argentina/Jujuy', 'America/Argentina/Jujuy'),
    ('America/Argentina/La_Rioja', 'America/Argentina/La_Rioja'),
    ('America/Argentina/Mendoza', 'America/Argentina/Mendoza'),
    ('America/Argentina/Rio_Gallegos', 'America/Argentina/Rio_Gallegos'),
    ('America/Argentina/Salta', 'America/Argentina/Salta'),
    ('America/Argentina/San_Juan', 'America/Argentina/San_Juan'),
    ('America/Argentina/San_Luis', 'America/Argentina/San_Luis'),
    ('America/Argentina/Tucuman', 'America/Argentina/Tucuman'),
    ('America/Argentina/Ushuaia', 'America/Argentina/Ushuaia'),
    ('America/Aruba', 'America/Aruba'),
    ('America/Asuncion', 'America/Asuncion'),
    ('America/Atikokan', 'America/Atikokan'),
    ('America/Bahia', 'America/Bahia'),
    ('America/Bahia_Banderas', 'America/Bahia_Banderas'),
    ('America/Barbados', 'America/Barbados'),
    ('America/Belem', 'America/Belem'),
    ('America/Belize', 'America/Belize'),
    ('America/Blanc-Sablon', 'America/Blanc-Sablon'),
    ('America/Boa_Vista', 'America/Boa_Vista'),
    ('America/Bogota', 'America/Bogota'),
    ('America/Boise', 'America/Boise'),
    ('America/Cambridge_Bay', 'America/Cambridge_Bay'),
    ('America/Campo_Grande', 'America/Campo_Grande'),
    ('America/Cancun', 'America/Cancun'),
    ('America/Caracas', 'America/Caracas'),
    ('America/Cayenne', 'America/Cayenne'),
    ('America/Cayman', 'America/Cayman'),
    ('America/Chicago', 'America/Chicago'),
    ('America/Chihuahua', 'America/Chihuahua'),
    ('America/Costa_Rica', 'America/Costa_Rica'),
    ('America/Creston', 'America/Creston'),
    ('America/Cuiaba', 'America/Cuiaba'),
    ('America/Curacao', 'America/Curacao'),
    ('America/Danmarkshavn', 'America/Danmarkshavn'),
    ('America/Dawson', 'America/Dawson'),
    ('America/Dawson_Creek', 'America/Dawson_Creek'),
    ('America/Denver', 'America/Denver'),
    ('America/Detroit', 'America/Detroit'),
    ('America/Dominica', 'America/Dominica'),
    ('America/Edmonton', 'America/Edmonton'),
    ('America/Eirunepe', 'America/Eirunepe'),
    ('America/El_Salvador', 'America/El_Salvador'),
    ('America/Fort_Nelson', 'America/Fort_Nelson'),
    ('America/Fortaleza', 'America/Fortaleza'),
    ('America/Glace_Bay', 'America/Glace_Bay'),
    ('America/Goose_Bay', 'America/Goose_Bay'),
    ('America/Grand_Turk', 'America/Grand_Turk'),
    ('America/Grenada', 'America/Grenada'),
    ('America/Guadeloupe', 'America/Guadeloupe'),
    ('America/Guatemala', 'America/Guatemala'),
    ('America/Guayaquil', 'America/Guayaquil'),
    ('America/Guyana', 'America/Guyana'),
    ('America/Halifax', 'America/Halifax'),
    ('America/Havana', 'America/Havana'),
    ('America/Hermosillo', 'America/Hermosillo'),
    ('America/Indiana/Indianapolis', 'America/Indiana/Indianapolis'),
    ('America/Indiana/Knox', 'America/Indiana/Knox'),
    ('America/Indiana/Marengo', 'America/Indiana/Marengo'),
    ('America/Indiana/Petersburg', 'America/Indiana/Petersburg'),
    ('America/Indiana/Tell_City', 'America/Indiana/Tell_City'),
    ('America/Indiana/Vevay', 'America/Indiana/Vevay'),
    ('America/Indiana/Vincennes', 'America/Indiana/Vincennes'),
    ('America/Indiana/Winamac', 'America/Indiana/Winamac'),
    ('America/Inuvik', 'America/Inuvik'),
    ('America/Iqaluit', 'America/Iqaluit'),
    ('America/Jamaica', 'America/Jamaica'),
    ('America/Juneau', 'America/Juneau'),
    ('America/Kentucky/Louisville', 'America/Kentucky/Louisville'),
    ('America/Kentucky/Monticello', 'America/Kentucky/Monticello'),
    ('America/Kralendijk', 'America/Kralendijk'),
    ('America/La_Paz', 'America/La_Paz'),
    ('America/Lima', 'America/Lima'),
    ('America/Los_Angeles', 'America/Los_Angeles'),
    ('America/Lower_Princes', 'America/Lower_Princes'),
    ('America/Maceio', 'America/Maceio'),
    ('America/Managua', 'America/Managua'),
    ('America/Manaus', 'America/Manaus'),
    ('America/Marigot', 'America/Marigot'),
    ('America/Martinique', 'America/Martinique'),
    ('America/Matamoros', 'America/Matamoros'),
    ('America/Mazatlan', 'America/Mazatlan'),
    ('America/Menominee', 'America/Menominee'),
    ('America/Merida', 'America/Merida'),
    ('America/Metlakatla', 'America/Metlakatla'),
    ('America/Mexico_City', 'America/Mexico_City'),
    ('America/Miquelon', 'America/Miquelon'),
    ('America/Moncton', 'America/Moncton'),
    ('America/Monterrey', 'America/Monterrey'),
    ('America/Montevideo', 'America/Montevideo'),
    ('America/Montserrat', 'America/Montserrat'),
    ('America/Nassau', 'America/Nassau'),
    ('America/New_York', 'America/New_York'),
    ('America/Nipigon', 'America/Nipigon'),
    ('America/Nome', 'America/Nome'),
    ('America/Noronha', 'America/Noronha'),
    ('America/North_Dakota/Beulah', 'America/North_Dakota/Beulah'),
    ('America/North_Dakota/Center', 'America/North_Dakota/Center'),
    ('America/North_Dakota/New_Salem', 'America/North_Dakota/New_Salem'),
    ('America/Nuuk', 'America/Nuuk'),
    ('America/Ojinaga', 'America/Ojinaga'),
    ('America/Panama', 'America/Panama'),
    ('America/Pangnirtung', 'America/Pangnirtung'),
    ('America/Paramaribo', 'America/Paramaribo'),
    ('America/Phoenix', 'America/Phoenix'),
    ('America/Port-au-Prince', 'America/Port-au-Prince'),
    ('America/Port_of_Spain', 'America/Port_of_Spain'),
    ('America/Porto_Velho', 'America/Porto_Velho'),
    ('America/Puerto_Rico', 'America/Puerto_Rico'),
    ('America/Punta_Arenas', 'America/Punta_Arenas'),
    ('America/Rainy_River', 'America/Rainy_River'),
    ('America/Rankin_Inlet', 'America/Rankin_Inlet'),
    ('America/Recife', 'America/Recife'),
    ('America/Regina', 'America/Regina'),
    ('America/Resolute', 'America/Resolute'),
    ('America/Rio_Branco', 'America/Rio_Branco'),
    ('America/Santarem', 'America/Santarem'),
    ('America/Santiago', 'America/Santiago'),
    ('America/Santo_Domingo', 'America/Santo_Domingo'),
    ('America/Sao_Paulo', 'America/Sao_Paulo'),
    ('America/Scoresbysund', 'America/Scoresbysund'),
    ('America/Sitka', 'America/Sitka'),
    ('America/St_Barthelemy', 'America/St_Barthelemy'),
    ('America/St_Johns', 'America/St_Johns'),
    ('America/St_Kitts', 'America/St_Kitts'),
    ('America/St_Lucia', 'America/St_Lucia'),
    ('America/St_Thomas', 'America/St_Thomas'),
    ('America/St_Vincent', 'America/St_Vincent'),
    ('America/Swift_Current', 'America/Swift_Current'),
    ('America/Tegucigalpa', 'America/Tegucigalpa'),
    ('America/Thule', 'America/Thule'),
    ('America/Thunder_Bay', 'America/Thunder_Bay'),
    ('America/Tijuana', 'America/Tijuana'),
    ('America/Toronto', 'America/Toronto'),
    ('America/Tortola', 'America/Tortola'),
    ('America/Vancouver', 'America/Vancouver'),
    ('America/Whitehorse', 'America/Whitehorse'),
    ('America/Winnipeg', 'America/Winnipeg'),
    ('America/Yakutat', 'America/Yakutat'),
    ('America/Yellowknife', 'America/Yellowknife'),
    ('Antarctica/Casey', 'Antarctica/Casey'),
    ('Antarctica/Davis', 'Antarctica/Davis'),
    ('Antarctica/DumontDUrville', 'Antarctica/DumontDUrville'),
    ('Antarctica/Macquarie', 'Antarctica/Macquarie'),
    ('Antarctica/Mawson', 'Antarctica/Mawson'),
    ('Antarctica/McMurdo', 'Antarctica/McMurdo'),
    ('Antarctica/Palmer', 'Antarctica/Palmer'),
    ('Antarctica/Rothera', 'Antarctica/Rothera'),
    ('Antarctica/Syowa', 'Antarctica/Syowa'),
    ('Antarctica/Troll', 'Antarctica/Troll'),
    ('Antarctica/Vostok', 'Antarctica/Vostok'),
    ('Arctic/Longyearbyen', 'Arctic/Longyearbyen'),
    ('Asia/Aden', 'Asia/Aden'),
    ('Asia/Almaty', 'Asia/Almaty'),
    ('Asia/Amman', 'Asia/Amman'),
    ('Asia/Anadyr', 'Asia/Anadyr'),
    ('Asia/Aqtau', 'Asia/Aqtau'),
    ('Asia/Aqtobe', 'Asia/Aqtobe'),
    ('Asia/Ashgabat', 'Asia/Ashgabat'),
    ('Asia/Atyrau', 'Asia/Atyrau'),
    ('Asia/Baghdad', 'Asia/Baghdad'),
    ('Asia/Bahrain', 'Asia/Bahrain'),
    ('Asia/Baku', 'Asia/Baku'),
    ('Asia/Bangkok', 'Asia/Bangkok'),
    ('Asia/Barnaul', 'Asia/Barnaul'),
    ('Asia/Beirut', 'Asia/Beirut'),
    ('Asia/Bishkek', 'Asia/Bishkek'),
    ('Asia/Brunei', 'Asia/Brunei'),
    ('Asia/Chita', 'Asia/Chita'),
    ('Asia/Choibalsan', 'Asia/Choibalsan'),
    ('Asia/Colombo', 'Asia/Colombo'),
    ('Asia/Damascus', 'Asia/Damascus'),
    ('Asia/Dhaka', 'Asia/Dhaka'),
    ('Asia/Dili', 'Asia/Dili'),
    ('Asia/Dubai', 'Asia/Dubai'),
    ('Asia/Dushanbe', 'Asia/Dushanbe'),
    ('Asia/Famagusta', 'Asia/Famagusta'),
    ('Asia/Gaza', 'Asia/Gaza'),
    ('Asia/Hebron', 'Asia/Hebron'),
    ('Asia/Ho_Chi_Minh', 'Asia/Ho_Chi_Minh'),
    ('Asia/Hong_Kong', 'Asia/Hong_Kong'),
    ('Asia/Hovd', 'Asia/Hovd'),
    ('Asia/Irkutsk', 'Asia/Irkutsk'),
    ('Asia/Jakarta', 'Asia/Jakarta'),
    ('Asia/Jayapura', 'Asia/Jayapura'),
    ('Asia/Jerusalem', 'Asia/Jerusalem'),
    ('Asia/Kabul', 'Asia/Kabul'),
    ('Asia/Kamchatka', 'Asia/Kamchatka'),
    ('Asia/Karachi', 'Asia/Karachi'),
    ('Asia/Kathmandu', 'Asia/Kathmandu'),
    ('Asia/Khandyga', 'Asia/Khandyga'),
    ('Asia/Kolkata', 'Asia/Kolkata'),
    ('Asia/Krasnoyarsk', 'Asia/Krasnoyarsk'),
    ('Asia/Kuala_Lumpur', 'Asia/Kuala_Lumpur'),
    ('Asia/Kuching', 'Asia/Kuching'),
    ('Asia/Kuwait', 'Asia/Kuwait'),
    ('Asia/Macau', 'Asia/Macau'),
    ('Asia/Magadan', 'Asia/Magadan'),
    ('Asia/Makassar', 'Asia/Makassar'),
    ('Asia/Manila', 'Asia/Manila'),
    ('Asia/Muscat', 'Asia/Muscat'),
    ('Asia/Nicosia', 'Asia/Nicosia'),
    ('Asia/Novokuznetsk', 'Asia/Novokuznetsk'),
    ('Asia/Novosibirsk', 'Asia/Novosibirsk'),
    ('Asia/Omsk', 'Asia/Omsk'),
    ('Asia/Oral', 'Asia/Oral'),
    ('Asia/Phnom_Penh', 'Asia/Phnom_Penh'),
    ('Asia/Pontianak', 'Asia/Pontianak'),
    ('Asia/Pyongyang', 'Asia/Pyongyang'),
    ('Asia/Qatar', 'Asia/Qatar'),
    ('Asia/Qostanay', 'Asia/Qostanay'),
    ('Asia/Qyzylorda', 'Asia/Qyzylorda'),
    ('Asia/Riyadh', 'Asia/Riyadh'),
    ('Asia/Sakhalin', 'Asia/Sakhalin'),
    ('Asia/Samarkand', 'Asia/Samarkand'),
    ('Asia/Seoul', 'Asia/Seoul'),
    ('Asia/Shanghai', 'Asia/Shanghai'),
    ('Asia/Singapore', 'Asia/Singapore'),
    ('Asia/Srednekolymsk', 'Asia/Srednekolymsk'),
    ('Asia/Taipei', 'Asia/Taipei'),
    ('Asia/Tashkent', 'Asia/Tashkent'),
    ('Asia/Tbilisi', 'Asia/Tbilisi'),
    ('Asia/Tehran', 'Asia/Tehran'),
    ('Asia/Thimphu', 'Asia/Thimphu'),
    ('Asia/Tokyo', 'Asia/Tokyo'),
    ('Asia/Tomsk', 'Asia/Tomsk'),
    ('Asia/Ulaanbaatar', 'Asia/Ulaanbaatar'),
    ('Asia/Urumqi', 'Asia/Urumqi'),
    ('Asia/Ust-Nera', 'Asia/Ust-Nera'),
    ('Asia/Vientiane', 'Asia/Vientiane'),
    ('Asia/Vladivostok', 'Asia/Vladivostok'),
    ('Asia/Yakutsk', 'Asia/Yakutsk'),
    ('Asia/Yangon', 'Asia/Yangon'),
    ('Asia/Yekaterinburg', 'Asia/Yekaterinburg'),
    ('Asia/Yerevan', 'Asia/Yerevan'),
    ('Atlantic/Azores', 'Atlantic/Azores'),
    ('Atlantic/Bermuda', 'Atlantic/Bermuda'),
    ('Atlantic/Canary', 'Atlantic/Canary'),
    ('Atlantic/Cape_Verde', 'Atlantic/Cape_Verde'),
    ('Atlantic/Faroe', 'Atlantic/Faroe'),
    ('Atlantic/Madeira', 'Atlantic/Madeira'),
    ('Atlantic/Reykjavik', 'Atlantic/Reykjavik'),
    ('Atlantic/South_Georgia', 'Atlantic/South_Georgia'),
    ('Atlantic/St_Helena', 'Atlantic/St_Helena'),
    ('Atlantic/Stanley', 'Atlantic/Stanley'),
    ('Australia/Adelaide', 'Australia/Adelaide'),
    ('Australia/Brisbane', 'Australia/Brisbane'),
    ('Australia/Broken_Hill', 'Australia/Broken_Hill'),
    ('Australia/Currie', 'Australia/Currie'),
    ('Australia/Darwin', 'Australia/Darwin'),
    ('Australia/Eucla', 'Australia/Eucla'),
    ('Australia/Hobart', 'Australia/Hobart'),
    ('Australia/Lindeman', 'Australia/Lindeman'),
    ('Australia/Lord_Howe', 'Australia/Lord_Howe'),
    ('Australia/Melbourne', 'Australia/Melbourne'),
    ('Australia/Perth', 'Australia/Perth'),
    ('Australia/Sydney', 'Australia/Sydney'),
    ('Canada/Atlantic', 'Canada/Atlantic'),
    ('Canada/Central', 'Canada/Central'),
    ('Canada/Eastern', 'Canada/Eastern'),
    ('Canada/Mountain', 'Canada/Mountain'),
    ('Canada/Newfoundland', 'Canada/Newfoundland'),
    ('Canada/Pacific', 'Canada/Pacific'),
    ('Europe/Amsterdam', 'Europe/Amsterdam'),
    ('Europe/Andorra', 'Europe/Andorra'),
    ('Europe/Astrakhan', 'Europe/Astrakhan'),
    ('Europe/Athens', 'Europe/Athens'),
    ('Europe/Belgrade', 'Europe/Belgrade'),
    ('Europe/Berlin', 'Europe/Berlin'),
    ('Europe/Bratislava', 'Europe/Bratislava'),
    ('Europe/Brussels', 'Europe/Brussels'),
    ('Europe/Bucharest', 'Europe/Bucharest'),
    ('Europe/Budapest', 'Europe/Budapest'),
    ('Europe/Busingen', 'Europe/Busingen'),
    ('Europe/Chisinau', 'Europe/Chisinau'),
    ('Europe/Copenhagen', 'Europe/Copenhagen'),
    ('Europe/Dublin', 'Europe/Dublin'),
    ('Europe/Gibraltar', 'Europe/Gibraltar'),
    ('Europe/Guernsey', 'Europe/Guernsey'),
    ('Europe/Helsinki', 'Europe/Helsinki'),
    ('Europe/Isle_of_Man', 'Europe/Isle_of_Man'),
    ('Europe/Istanbul', 'Europe/Istanbul'),
    ('Europe/Jersey', 'Europe/Jersey'),
    ('Europe/Kaliningrad', 'Europe/Kaliningrad'),
    ('Europe/Kiev', 'Europe/Kiev'),
    ('Europe/Kirov', 'Europe/Kirov'),
    ('Europe/Lisbon', 'Europe/Lisbon'),
    ('Europe/Ljubljana', 'Europe/Ljubljana'),
    ('Europe/London', 'Europe/London'),
    ('Europe/Luxembourg', 'Europe/Luxembourg'),
    ('Europe/Madrid', 'Europe/Madrid'),
    ('Europe/Malta', 'Europe/Malta'),
    ('Europe/Mariehamn', 'Europe/Mariehamn'),
    ('Europe/Minsk', 'Europe/Minsk'),
    ('Europe/Monaco', 'Europe/Monaco'),
    ('Europe/Moscow', 'Europe/Moscow'),
    ('Europe/Oslo', 'Europe/Oslo'),
    ('Europe/Paris', 'Europe/Paris'),
    ('Europe/Podgorica', 'Europe/Podgorica'),
    ('Europe/Prague', 'Europe/Prague'),
    ('Europe/Riga', 'Europe/Riga'),
    ('Europe/Rome', 'Europe/Rome'),
    ('Europe/Samara', 'Europe/Samara'),
    ('Europe/San_Marino', 'Europe/San_Marino'),
    ('Europe/Sarajevo', 'Europe/Sarajevo'),
    ('Europe/Saratov', 'Europe/Saratov'),
    ('Europe/Simferopol', 'Europe/Simferopol'),
    ('Europe/Skopje', 'Europe/Skopje'),
    ('Europe/Sofia', 'Europe/Sofia'),
    ('Europe/Stockholm', 'Europe/Stockholm'),
    ('Europe/Tallinn', 'Europe/Tallinn'),
    ('Europe/Tirane', 'Europe/Tirane'),
    ('Europe/Ulyanovsk', 'Europe/Ulyanovsk'),
    ('Europe/Uzhgorod', 'Europe/Uzhgorod'),
    ('Europe/Vaduz', 'Europe/Vaduz'),
    ('Europe/Vatican', 'Europe/Vatican'),
    ('Europe/Vienna', 'Europe/Vienna'),
    ('Europe/Vilnius', 'Europe/Vilnius'),
    ('Europe/Volgograd', 'Europe/Volgograd'),
    ('Europe/Warsaw', 'Europe/Warsaw'),
    ('Europe/Zagreb', 'Europe/Zagreb'),
    ('Europe/Zaporozhye', 'Europe/Zaporozhye'),
    ('Europe/Zurich', 'Europe/Zurich'),
    ('GMT', 'GMT'),
    ('Indian/Antananarivo', 'Indian/Antananarivo'),
    ('Indian/Chagos', 'Indian/Chagos'),
    ('Indian/Christmas', 'Indian/Christmas'),
    ('Indian/Cocos', 'Indian/Cocos'),
    ('Indian/Comoro', 'Indian/Comoro'),
    ('Indian/Kerguelen', 'Indian/Kerguelen'),
    ('Indian/Mahe', 'Indian/Mahe'),
    ('Indian/Maldives', 'Indian/Maldives'),
    ('Indian/Mauritius', 'Indian/Mauritius'),
    ('Indian/Mayotte', 'Indian/Mayotte'),
    ('Indian/Reunion', 'Indian/Reunion'),
    ('Pacific/Apia', 'Pacific/Apia'),
    ('Pacific/Auckland', 'Pacific/Auckland'),
    ('Pacific/Bougainville', 'Pacific/Bougainville'),
    ('Pacific/Chatham', 'Pacific/Chatham'),
    ('Pacific/Chuuk', 'Pacific/Chuuk'),
    ('Pacific/Easter', 'Pacific/Easter'),
    ('Pacific/Efate', 'Pacific/Efate'),
    ('Pacific/Enderbury', 'Pacific/Enderbury'),
    ('Pacific/Fakaofo', 'Pacific/Fakaofo'),
    ('Pacific/Fiji', 'Pacific/Fiji'),
    ('Pacific/Funafuti', 'Pacific/Funafuti'),
    ('Pacific/Galapagos', 'Pacific/Galapagos'),
    ('Pacific/Gambier', 'Pacific/Gambier'),
    ('Pacific/Guadalcanal', 'Pacific/Guadalcanal'),
    ('Pacific/Guam', 'Pacific/Guam'),
    ('Pacific/Honolulu', 'Pacific/Honolulu'),
    ('Pacific/Kiritimati', 'Pacific/Kiritimati'),
    ('Pacific/Kosrae', 'Pacific/Kosrae'),
    ('Pacific/Kwajalein', 'Pacific/Kwajalein'),
    ('Pacific/Majuro', 'Pacific/Majuro'),
    ('Pacific/Marquesas', 'Pacific/Marquesas'),
    ('Pacific/Midway', 'Pacific/Midway'),
    ('Pacific/Nauru', 'Pacific/Nauru'),
    ('Pacific/Niue', 'Pacific/Niue'),
    ('Pacific/Norfolk', 'Pacific/Norfolk'),
    ('Pacific/Noumea', 'Pacific/Noumea'),
    ('Pacific/Pago_Pago', 'Pacific/Pago_Pago'),
    ('Pacific/Palau', 'Pacific/Palau'),
    ('Pacific/Pitcairn', 'Pacific/Pitcairn'),
    ('Pacific/Pohnpei', 'Pacific/Pohnpei'),
    ('Pacific/Port_Moresby', 'Pacific/Port_Moresby'),
    ('Pacific/Rarotonga', 'Pacific/Rarotonga'),
    ('Pacific/Saipan', 'Pacific/Saipan'),
    ('Pacific/Tahiti', 'Pacific/Tahiti'),
    ('Pacific/Tarawa', 'Pacific/Tarawa'),
    ('Pacific/Tongatapu', 'Pacific/Tongatapu'),
    ('Pacific/Wake', 'Pacific/Wake'),
    ('Pacific/Wallis', 'Pacific/Wallis'),
    ('US/Alaska', 'US/Alaska'),
    ('US/Arizona', 'US/Arizona'),
    ('US/Central', 'US/Central'),
    ('US/Eastern', 'US/Eastern'),
    ('US/Hawaii', 'US/Hawaii'),
    ('US/Mountain', 'US/Mountain'),
    ('US/Pacific', 'US/Pacific'),
    ('UTC', 'UTC')
]


BANNED_WORDS = [
    "ballsack",
    "bastard",
    "bitch",
    "blowjob",
    "boner",
    "clitoris",
    "cunt",
    "dyke",
    "fag",
    "fuck",
    "nigger",
    "nigga",
    "penis",
    "pussy",
    "scrotum",
    "shit",
    "sh1t",
]




""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BLEACH ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def bleach_before_database(html):
    try:
        html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    except: pass
    try:
        html = bleach.clean(html,tags=[], strip=True)
    except: pass
    try:
        html = html.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    except: pass
    return html


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EMAIL ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def get_time_zone_for_email(this_profile, this_event):
    """ 
    Get user's time_zone 
    """

    # get time zone
    try:
        local_timezone = pytz.timezone(attendee.time_zone)
    except:
        local_timezone = None                    

    if local_timezone is None:
        try:
            local_timezone = pytz.timezone(event.time_zone)
        except:
            local_timezone = None                    

    return local_timezone


def make_event_subject(initial_string, event_name):
    """
    Makes subject for email < 70 characters
    """

    inital_string_length = len(initial_string)
    event_name_length = len(event_name)

    if inital_string_length > 70:
        return initial_string[:70] + "..."

    elif inital_string_length + event_name_length > 70:
        return initial_string + event_name[:70-inital_string_length] + "..."

    else:
        return initial_string + event_name


def make_event_email_body(this_event, local_timezone):
    """
    Make the body of the email.
    """

    # get start time in local time zone if possible
    if local_timezone is not None:
        event_start_time = this_event.start_time.astimezone(local_timezone).strftime("%B %-d, %Y %-I:%M %p %Z")
    else:
        event_start_time = this_event.start_time.astimezone(pytz.timezone("America/New_York")).strftime("%B %-d, %Y %-I:%M %p %Z")

    this_event_url = this_event.get_video_chat_url()
    if this_event_url == None:
        this_event_url = "No URL provided yet.  Please check event page for updates."

    # make email body
    event_email_body = "<br><br>"
    event_email_body += "YapSpot.com Event<br>"
    event_email_body += "----------------------------------"
    event_email_body += "<br><br>"

    event_email_body += "EVENT:"
    event_email_body += "<br>"
    event_email_body += this_event.name
    event_email_body += "<br><br>"

    event_email_body += "EVENT VIDEOCHAT URL:"
    event_email_body += "<br>(click to enter videochat room)"
    event_email_body += "<br>"
    event_email_body += this_event_url
    event_email_body += "<br><br>"

    event_email_body += "EVENT START TIME:"
    event_email_body += "<br>"
    event_email_body += event_start_time
    event_email_body += "<br><br>"

    event_email_body += "EVENT PAGE:"
    event_email_body += "<br>"
    event_email_body += "https://www.YapSpot.com" + reverse('eventview', kwargs={"event_id":this_event.pk})
    event_email_body += "<br><br>"

    event_email_body += "EVENT GROUP:"
    event_email_body += "<br>"
    event_email_body += this_event.group.__str__()
    event_email_body += "<br><br>"

    event_email_body += "EVENT HOST:"
    event_email_body += "<br>"
    event_email_body += this_event.admin.__str__()
    event_email_body += "<br><br>"

    event_email_body += "EVENT DESCRIPTION:"
    event_email_body += "<br>"
    event_email_body += this_event.description
    event_email_body += "<br><br>"
    event_email_body += "<br><br>"
    event_email_body += "If you no longer want to receive emails from YapSpot.com.  Please login and edit your profile to opt-out: "
    event_email_body += "<br>https://www.YapSpot.com/yap/profileedit/"

    return event_email_body


def send_event_email(email_subject, email_body, email_of_recipient, DJANGO_ENV):
    """
    Actually send the email.
    """
    sent_successfully = False

    # send email
    if DJANGO_ENV == "PROD":
        try:
            email = EmailMessage(email_subject, 
                                 email_body, 
                                 'hello@yapspot.com', 
                                 [email_recipient]
                                 )
            email.content_subtype = "html"
            email.send() 

            # for returning
            sent_successfully = True

        except:
            print("Crontab -- Error sending email.")

    else:
        print("Crontab -- Email Reminder: " + email_subject)
        email = EmailMessage(email_subject, 
                             email_body, 
                             'hello@yapspot.com', 
                             ["kevinwoodson@gmail.com"]
                             )
        email.content_subtype = "html"
        email.send() 

        # for returning
        sent_successfully = True

    return sent_successfully



def make_and_send_event_email(this_profile, this_event, initial_string_email_subject, DJANGO_ENV, is_hosting = False):
    """
    Makes and sends an email using functions above
    """

    # only send emails to verified email addresses.
    if not EmailAddress.objects.filter(user=this_profile.user, verified=True).exists():
        return False

    # return if they opted out of receiving emails.
    if not this_profile.accept_email:
        return True

    # to avoid sending the email twice.
    if not is_hosting and this_event.determine_if_reminder_email_sent_pre_event(this_profile):
        return True

    # first get local time zone
    local_timezone = get_time_zone_for_email(this_profile, this_event)
    # make subject for the email
    email_subject = make_event_subject(initial_string_email_subject, this_event.name)
    # then get the body of the email
    email_body = make_event_email_body(this_event, local_timezone)
    # then send the email.

    if is_hosting:
        beginning_string_for_admin = "<br><br><h3>The event you're hosting is beginning in 30 minutes.  The below email will be sent to attendees in 15 minutes."
        beginning_string_for_admin += "<br>Please ensure that the event videochat URL and/or description below clearly describe how to find your event."
        beginning_string_for_admin += "<br>If not, log in and edit the event to describe clearly how to find the videochat room."
        beginning_string_for_admin += "<br>Thank you.</h3><br>"
        email_body = beginning_string_for_admin + email_body

    sent_successfully = send_event_email(email_subject, email_body, this_profile.user.email, DJANGO_ENV)

    if  not is_hosting and sent_successfully:
        this_event.set_reminder_email_sent_pre_event(this_profile)

    return True



