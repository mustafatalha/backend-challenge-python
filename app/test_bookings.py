import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

GUEST_A_UNIT_1: dict = {
    'unit_id': '1', 'guest_name': 'GuestA', 'check_in_date': datetime.date.today().strftime('%Y-%m-%d'),
    'number_of_nights': 5
}
GUEST_A_UNIT_2: dict = {
    'unit_id': '2', 'guest_name': 'GuestA', 'check_in_date': datetime.date.today().strftime('%Y-%m-%d'),
    'number_of_nights': 5
}
GUEST_B_UNIT_1: dict = {
    'unit_id': '1', 'guest_name': 'GuestB', 'check_in_date': datetime.date.today().strftime('%Y-%m-%d'),
    'number_of_nights': 5
}


@pytest.fixture()
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.freeze_time('2023-05-21')
def test_create_fresh_booking(test_db):
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    response.raise_for_status()
    assert response.status_code == 200, response.text


@pytest.mark.freeze_time('2023-05-21')
def test_same_guest_same_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text
    response.raise_for_status()

    # Guests want to book same unit again
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'The given guest name cannot book the same unit multiple times'


@pytest.mark.freeze_time('2023-05-21')
def test_same_guest_different_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # Guest wants to book another unit
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_2
    )
    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'The same guest cannot be in multiple units at the same time'


@pytest.mark.freeze_time('2023-05-21')
def test_different_guest_same_unit_booking(test_db):
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # GuestB trying to book a unit that is already occuppied
    response = client.post(
        "/api/v1/booking",
        json=GUEST_B_UNIT_1
    )
    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'For the given check-in date, the unit is already occupied'


@pytest.mark.freeze_time('2023-05-21')
def test_different_guest_same_unit_booking_different_date(test_db):
    guess_a_unit_1: dict = GUEST_A_UNIT_1.copy()
    guess_a_unit_1['check_in_date'] = datetime.date.today().strftime('%Y-%m-%d')

    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=guess_a_unit_1
    )
    assert response.status_code == 200, response.text

    # GuestB trying to book a unit that is already occuppied
    response = client.post(
        "/api/v1/booking",
        json={
            'unit_id': '1',  # same unit
            'guest_name': 'GuestB',  # different guest
            # check_in date of GUEST A + 1, the unit is already booked on this date
            'check_in_date': (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'),
            'number_of_nights': 5
        }
    )
    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'For the given check-in date, the unit is already occupied'


def test_get_bookings(test_db):
    # Create booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # Get booking with both unit_id and guest_name
    response = client.get(
        "/api/v1/booking",
        params={
            'unit_id': GUEST_A_UNIT_1.get('unit_id'),
            'guest_name': GUEST_A_UNIT_1.get('guest_name')
        }
    )
    assert response.json() == GUEST_A_UNIT_1

    # Get bookings with only guest_name
    response = client.get(
        "/api/v1/booking",
        params={
            'guest_name': GUEST_A_UNIT_1.get('guest_name')
        }
    )
    assert response.json() == [GUEST_A_UNIT_1]

    # Get bookings with only unit_id
    response = client.get(
        "/api/v1/booking",
        params={
            'unit_id': GUEST_A_UNIT_1.get('unit_id')
        }
    )
    assert response.json() == [GUEST_A_UNIT_1]




def test_booking_extension_happy_path(test_db):
    # Create booking
    response = client.post(
        "/api/v1/booking",
        json=GUEST_A_UNIT_1
    )
    assert response.status_code == 200, response.text

    # Extend stay
    response = client.post(
        "/api/v1/booking/extension",
        params={
            'guest_name': GUEST_A_UNIT_1.get('guest_name'),
            'unit_id': GUEST_A_UNIT_1.get('unit_id'),
            'extra_nights': 7,
        }
    )

    assert response.status_code == 200, response.text


@pytest.mark.freeze_time('2023-05-21')
def test_booking_extension_unit_unavailable(test_db):
    guess_a_unit_1: dict = GUEST_A_UNIT_1.copy()
    guess_a_unit_1['check_in_date'] = datetime.date.today().strftime('%Y-%m-%d')
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=guess_a_unit_1
    )
    assert response.status_code == 200, response.text

    # Create 2nd booking same unit but later date
    response = client.post(
        "/api/v1/booking",
        json={
            'unit_id': guess_a_unit_1.get('unit_id'),  # same unit
            'guest_name': 'GuestB',  # different guest
            'check_in_date': (datetime.date.today()
                              + datetime.timedelta(2 + guess_a_unit_1.get("number_of_nights"))).strftime('%Y-%m-%d'),
            'number_of_nights': 5
        }
    )
    assert response.status_code == 200, response.text

    # Test 'For the extension period, the unit is already occupied'
    response = client.post(
        "/api/v1/booking/extension",
        params={
            'guest_name': guess_a_unit_1.get('guest_name'),
            'unit_id': guess_a_unit_1.get('unit_id'),
            'extra_nights': 15,
        }
    )

    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'For the extension period, the unit is already occupied'


@pytest.mark.freeze_time('2023-05-21')
def test_booking_extension_same_guest_different_unit(test_db):
    guess_a_unit_1: dict = GUEST_A_UNIT_1.copy()
    guess_a_unit_1['check_in_date'] = datetime.date.today().strftime('%Y-%m-%d')
    # Create first booking
    response = client.post(
        "/api/v1/booking",
        json=guess_a_unit_1
    )
    assert response.status_code == 200, response.text

    # Create 2nd booking same unit but later date
    response = client.post(
        "/api/v1/booking",
        json={
            'unit_id': "6",  # another unit
            'guest_name': guess_a_unit_1.get('guest_name'),  # same guest
            'check_in_date': (datetime.date.today()
                              + datetime.timedelta(2 + guess_a_unit_1.get("number_of_nights"))).strftime('%Y-%m-%d'),
            'number_of_nights': 5
        }
    )
    assert response.status_code == 200, response.text

    # Test 'For the extension period, the unit is already occupied'
    response = client.post(
        "/api/v1/booking/extension",
        params={
            'guest_name': guess_a_unit_1.get('guest_name'),
            'unit_id': guess_a_unit_1.get('unit_id'),
            'extra_nights': 15,
        }
    )

    assert response.status_code == 400, response.text
    assert response.json()['detail'] == 'The same guest cannot be in multiple units at the same time'