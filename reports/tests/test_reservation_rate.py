import pytest

from django.test import override_settings

from resources.models import Unit, Resource, Reservation
from resources.tests.conftest import *

url = '/reports/reservation_rate/'

@pytest.fixture
def reservation(resource_in_unit, user):
    return Reservation.objects.create(
        resource=resource_in_unit,
        begin='2015-04-04T09:00:00+02:00',
        end='2015-04-04T10:00:00+02:00',
        user=user,
        reserver_name='John Smith',
        event_subject="John's welcome party",
    )


def check_valid_response(response, reservation):
    headers = response._headers
    assert headers['content-type'][1] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert headers['content-disposition'][1].endswith('.xlsx')
    content = str(response.content)

    assert len(content) > 0


@pytest.mark.django_db
def test_get_reservation_rate_report(api_client, reservation):
    response = api_client.get(
        f"{url}?units={reservation.resource.unit.id}&start_date=2015-04-01&end_date=2015-04-06&start_time=08:00&end_time=16:00"
    )
    assert response.status_code == 200

    check_valid_response(response, reservation)


@pytest.mark.django_db
@override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
def test_reservation_rate_filter_errors(api_client, test_unit, reservation, resource_in_unit):
    response = api_client.get(
        f"{url}?&start_date=2015-04-01&end_date=2015-04-06&start_time=08:00&end_time=16:00"
    )
    assert response.status_code == 400
    assert "Missing unit id(s)" in response.data

    response = api_client.get(
        f"{url}?units={reservation.resource.unit.id}&end_date=2015-04-06&start_time=08:00&end_time=16:00"
    )
    assert response.status_code == 400
    assert "Missing start date or end date" in response.data

    response = api_client.get(
        f"{url}?units={reservation.resource.unit.id}&start_date=3-04-01&end_date=2015-04-06&start_time=08:00&end_time=16:00"
    )
    assert response.status_code == 400
    assert "Dates be in Y-m-d format and times must be in H:M format" in response.data
