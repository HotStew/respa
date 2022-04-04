import pytest
from django.utils.encoding import force_text
from lxml.builder import E

from respa_exchange.downloader import sync_from_exchange
from respa_exchange.ews.session import SoapFault
from respa_exchange.ews.xml import S
from respa_exchange.models import ExchangeResource
from respa_exchange.tests.session import SoapSeller


class EverythingFails(object):
    code = 'nope'
    text = 'Das ist foreboden'

    def handle_everything(self, request):
        return S.Fault(
            E.faultcode(self.code),
            E.faultstring(self.text),
        )
