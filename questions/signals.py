''' Django notifications signal file '''
# -*- coding: utf-8 -*-
from django.dispatch import Signal

ask = Signal(providing_args=[  # pylint: disable=invalid-name
    'answer', 'actor', 'verb', 'action', 'target', 'description',
    'created', 'level'
])
