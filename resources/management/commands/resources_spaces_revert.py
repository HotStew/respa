import csv
import enum
import os

from django.core.management import BaseCommand, CommandError

from resources.models import Resource


class Columns(enum.Enum):
    is_public = 0
    unit = 1
    recourse_type = 2
    purpose = 3
    name = 4
    description = 5
    authentication_type = 6
    people_capacity = 7
    area = 8
    min_period = 9
    max_period = 10
    is_reservable = 11
    reservation_info = 12
    resource_group = 13
    exchange = 14


class Command(BaseCommand):
    help = "Delete resources imported from CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", help="Path to the csv file",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]

        if not os.path.exists(file_path):
            raise CommandError("File {0} does not exist".format(file_path))

        with open(file_path) as f:
            csv_reader = csv.reader(f, delimiter=";")
            resources = []
            print("Processing...")
            for idx, row in enumerate(csv_reader):
                if idx == 0 or not row[Columns.name.value]:
                    continue
                resources.append(row[Columns.name.value])
            print("** Resources marked for deletion **\n")
            print(*resources, sep='\n')

            confirmation = input("\nDelete objects?: ")

            if confirmation == "yes":
                for resource in resources:
                    print("Deleting object %s" % resource)
                    Resource.objects.filter(name=resource).delete()
                    print("%s deleted." % resource)
