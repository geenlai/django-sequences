# -*- coding: utf-8 -*-

from django.db import connections, router, transaction


UPSERT_QUERY = """
    INSERT INTO sequences_sequence (name, last)
         VALUES (%s, %s)
    ON CONFLICT (name)
  DO UPDATE SET last = sequences_sequence.last + %s
      RETURNING last
"""


def get_next_value(
        sequence_name='default', initial_value=1, reset_value=None, nowait=False, using=None):
    """
    Return the next value for a given sequence.
    """
    # Inner import because models cannot be imported before their application.
    from .models import Sequence

    if reset_value is not None:
        assert initial_value < reset_value

    if using is None:
        using = router.db_for_write(Sequence)

    connection = connections[using]

    if (getattr(connection, 'pg_version', 0) >= 90500 and reset_value is None and not nowait):

        # PostgreSQL ≥ 9.5 supports "upsert".

        with connection.cursor() as cursor:
            cursor.execute(UPSERT_QUERY, [sequence_name, initial_value, 1])
            last, = cursor.fetchone()
        return last

    else:

        # Other databases require making more database queries.

        with transaction.atomic(using=using, savepoint=False):
            sequence, created = (
                Sequence.objects
                        .select_for_update(nowait=nowait)
                        .get_or_create(name=sequence_name,
                                       defaults={'last': initial_value})
            )

            if not created:
                sequence.last += 1
                if reset_value is not None and sequence.last >= reset_value:
                    sequence.last = initial_value
                sequence.save()

            return sequence.last


def get_next_n_value(size, sequence_name='default', initial_value=1, nowait=False, using=None):
    """
    Return the next n values for a given sequence.
    :param sequence_name: 序列名称
    :param initial_value: 初始值
    :param nowait:
    :param using:
    :param size:
    :return:
    """
    from .models import Sequence

    if using is None:
        using = router.db_for_write(Sequence)

    connection = connections[using]

    if (getattr(connection, 'pg_version', 0) >= 90500 and False and not nowait):
        # PostgreSQL ≥ 9.5 supports "upsert".

        with connection.cursor() as cursor:
            cursor.execute(UPSERT_QUERY, [sequence_name, initial_value + size - 1, size])
            last, = cursor.fetchone()
            return list(range(last - size + 1, last + 1))
    else:

        # Other databases require making more database queries.

        with transaction.atomic(using=using, savepoint=False):
            sequence, created = (
                Sequence.objects
                        .select_for_update(nowait=nowait)
                        .get_or_create(name=sequence_name,
                                       defaults={'last': initial_value + size - 1})
            )

            if not created:
                sequence.last += size
                sequence.save()
            else:
                if sequence.last == 1:
                    return list(range(1, size + 1))
            return list(range(sequence.last - size + 1, sequence.last + 1))
