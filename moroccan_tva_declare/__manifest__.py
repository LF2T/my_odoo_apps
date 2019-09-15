# -*- coding: utf-8 -*-


{
    'name': 'Teledeclaration TVA',

    'description': "Ce module permet l'export du fichier EDI pour la télédéclaration des Entreprises Marocaines,"
                    "A partir des lignes de Facture déjà existantes sur Odoo Comptabilite. ",

    "version": "12.0.1.0.0",
    "development_status": "Stable",
    "category": "Accounting",

    'price': 19.99,
    'currency': 'EUR',

    'author': 'El Mehdi LAFTOUTY',

    'depends': ['account',
                ],

    'data': [
            'views/tva_declare.xml',
            'views/generate_xml_view.xml',
            'security/ir.model.access.csv',
             ],

    'js': ['static/src/js/variant.js'],

    'qweb': ['static/src/xml/view.xml'],

    'application': 'True'

}
