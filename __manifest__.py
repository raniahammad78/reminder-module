{
    'name': 'Remainder Module',
    'version': '18.0.1.0.0',
    'summary': 'Tracks product remainders, quantity, and price for products or license',
    'sequence': 1,
    'category': 'Sales',
    'author': 'RANIA',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        "security/ir.model.access.csv",
        "data/remainder_automation.xml",
        "report/remainder_report.xml",
        'views/remainder_views.xml',
        "views/remainder_menus.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
