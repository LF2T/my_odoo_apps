# -*- coding: utf-8 -*-
{
    'name' : 'Project Surveys Answers',
    'author': 'Infomineo',
    'version' : '1.0',
    'summary': 'Survey Answers',
    'sequence': 35,
    'description': """
 - Formats the Answers and Shows them in the Backend.
 - Allows Group By Team Member, Project and Page.
    """,
    'category': 'Survey',
    'website': 'https://infomineo.com/',
    'images': [],
    'depends': ['survey', 'project'],
    'data': [
        'views/survey_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
