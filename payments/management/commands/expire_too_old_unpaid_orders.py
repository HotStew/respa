import logging
import sys

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from payments.models import Order

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sets too old orders from state "waiting" to state "expired".'

    @atomic
    def handle(self, *args, **options):
        logging.basicConfig(
            level = logging.INFO,
            format = "%(asctime)s %(message)s",
            datefmt = "%Y-%m-%d %H:%M:%S",
            stream = sys.stdout
        )
        logger.info('Expiring too old unpaid orders...')
        num_of_updated_orders = Order.objects.update_expired()
        logger.info('Done, {} order(s) got expired.'.format(num_of_updated_orders))
