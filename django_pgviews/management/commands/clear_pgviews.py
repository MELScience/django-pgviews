import logging

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections

from django_pgviews.view import clear_view, View, MaterializedView


log = logging.getLogger("django_pgviews.sync_pgviews")


class Command(BaseCommand):
    help = """Clear Postgres views. Use this before running a migration"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. Defaults to the "default" database.',
        )

    def handle(self, **options):
        """
        """
        # Get the database we're operating from
        db = options["database"]
        connection = connections[db]
        for view_cls in apps.get_models():
            if not (isinstance(view_cls, type) and issubclass(view_cls, View) and hasattr(view_cls, "sql")):
                continue
            python_name = "{}.{}".format(view_cls._meta.app_label, view_cls.__name__)
            status = clear_view(
                connection, view_cls._meta.db_table, materialized=isinstance(view_cls(), MaterializedView)
            )
            if status == "DROPPED":
                msg = "dropped"
            else:
                msg = "not dropped"
            log.info(
                "%(python_name)s (%(view_name)s): %(msg)s"
                % {"python_name": python_name, "view_name": view_cls._meta.db_table, "msg": msg}
            )
