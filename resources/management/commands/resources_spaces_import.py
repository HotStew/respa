import csv
import enum
import os

from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import translation

from resources.models import Resource, Unit, ResourceType, Purpose, ResourceGroup
from resources.models.reservation import ReservationMetadataSet
from respa_exchange.models import ExchangeConfiguration, ExchangeResource


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
    help = "Import resources via csv file. This is for importing resources for spaces"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", help="Path to the csv file",
        )

        parser.add_argument(
            "--default_reservation_metadata_set", help="Default reservation metadata set to use", nargs="?", default="default"
        )

    @staticmethod
    def get_authentication_type(authentication_type_fi):
        if authentication_type_fi.lower() == "ei mitään":
            return "none"
        with translation.override("fi"):
            authentication_type = dict(Resource.AUTHENTICATION_TYPES)
            name = [k for k in authentication_type.keys() if
                    authentication_type[k] == authentication_type_fi]
            return name[0]

    def handle(self, *args, **options):
        file_path = options["file_path"]
        default_reservation_metadata_set = options["default_reservation_metadata_set"]

        if not os.path.exists(file_path):
            raise CommandError("File {0} does not exist".format(file_path))

        with open(file_path) as f:
            csv_reader = csv.reader(f, delimiter=";")
            print("Processing...")
            with transaction.atomic():
                for idx, row in enumerate(csv_reader):
                    if idx == 0 or not row[Columns.name.value]:
                        continue

                    unit, created = Unit.objects.update_or_create(
                        street_address__iexact=row[Columns.unit.value],
                        defaults={'name': row[Columns.unit.value].split(",")[0],
                                'street_address': row[Columns.unit.value]})

                    resource_type, created = ResourceType.objects.update_or_create(
                        name__iexact=row[Columns.recourse_type.value],
                        main_type="space",
                        defaults={'name': row[Columns.recourse_type.value]}
                    )

                    resource_data = {
                        "public": True if row[Columns.is_public.value] else False,
                        "unit": unit,
                        "type": resource_type,
                        "name": row[Columns.name.value],
                        "description": row[Columns.description.value],
                        "authentication": self.get_authentication_type(row[Columns.authentication_type.value]),
                        "people_capacity": None if row[Columns.people_capacity.value] == "" else row[Columns.people_capacity.value],
                        "area": None if row[Columns.area.value] == "" else row[Columns.area.value],
                        "reservable": True if row[Columns.is_reservable.value] else False,
                        "reservation_info": row[Columns.reservation_info.value],
                        "reservation_metadata_set": ReservationMetadataSet.objects.get(name=default_reservation_metadata_set)
                    }

                    if row[Columns.min_period.value]:
                        min_period = {
                            "min_period": row[Columns.min_period.value]
                        }
                        resource_data.update(min_period)

                    if row[Columns.max_period.value]:
                        max_period = {
                            "max_period": row[Columns.max_period.value]
                        }
                        resource_data.update(max_period)

                    resource, created = Resource.objects.update_or_create(
                        name__iexact=row[Columns.name.value],
                        defaults=resource_data
                    )

                    purpose, created = Purpose.objects.update_or_create(
                        name__iexact=row[Columns.purpose.value],
                        defaults={'name': row[Columns.purpose.value]})
                    resource.purposes.add(purpose)

                    resource_groups = set(
                    rg.strip()
                        for rg in row[Columns.resource_group.value].split(",")
                    )
                    resource_groups.add("kanslia")

                    for resource_group_name in resource_groups:
                        resource_group, created = ResourceGroup.objects.update_or_create(
                            name__iexact=resource_group_name,
                            defaults={'name': resource_group_name},
                        )
                        resource_group.resources.add(resource)

                    exchange_configuration_count = ExchangeConfiguration.objects.count()
                    if exchange_configuration_count is not 0:
                        if row[Columns.exchange.value] is not '':
                            exchange_configuration = ExchangeConfiguration.objects.first()
                            ExchangeResource.objects.update_or_create(
                                principal_email__iexact=row[Columns.exchange.value],
                                defaults={'principal_email': row[Columns.exchange.value], 'resource_id': resource.pk,
                                        'exchange_id': exchange_configuration.pk})
                    else:
                        print('Can not find exchange_configuration. Skipping add exchange resource')
                print("Done!")
