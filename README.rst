django-sequences
################

The problem
===========

Django's default, implicit primary keys aren't guaranteed to be sequential.

If a transaction inserts a row and then is rolled back, the sequence counter
isn't rolled back for performance reasons, creating a gap in primary keys.

This can cause compliance issues for some use cases such as accounting.

This risk isn't well known. Since most transactions succeed, values look
sequential. Gaps will only be revealed by audits.

The solution
============

django-sequences provides just two function, ``get_next_value`` and ``get_next_n_value``,
which is designed to be used as follows::

    from django.db import transaction

    from sequences import get_next_value

    from invoices.models import Invoice

    with transaction.atomic():
        Invoice.objects.create(number=get_next_value('invoice_numbers'))

**The guarantees of django-sequences only apply if you call** ``get_next_value``
**and save its return value to the database within the same transaction!**

Installation
============

Install django-sequences::

    cat requirements.txt
    --trusted-host=pypi.luojilab.com
    --index-url http://pypi.luojilab.com/rock2018/pypi

    django-sequences=0.1.5    # 请安装最新版本
    pip install -r requirements.txt
    $ pip install django-sequences

Add it to the list of applications in your project's settings::

    INSTALLED_APPS = [
    '...',
    'sequences',
]


Run migrations::

    $ ./manage.py migrate

API
===

``get_next_value`` generates a gap-less sequence of integer values::

    >>> get_next_value()
    1
    >>> get_next_value()
    2
    >>> get_next_value()
    3

It supports multiple independent sequences::

    >>> get_next_value('PO')
    1
    >>> get_next_value('PO')
    2
    >>> get_next_value('PO')
    1
    >>> get_next_value('PO')
    2

It supports multiple values sequences::

    >>> get_next_n_value(5, 'PO')
    [0, 1, 2, 3, 4]
    >>> get_next_value(5, 'PO')
    [5, 6, 7, 8, 9]
    >>> get_next_n_value(5, 'SO')
    [0, 1, 2, 3, 4]
    >>> get_next_value(5, 'SO')
    [5, 6, 7, 8, 9]
