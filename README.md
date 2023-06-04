# Backend test

### Updates
#### Bug Fixes
There were 2 bugs at the crud layer and 1 test error.
- It was only checking guest_name at Check-2 of is_booking_possible func. This is not enough since a customer may do booking several times to different units. So, I added a computed property to BookingBase and a check_out_date column to the database. Then I added checking of period to is_booking_possible Check-2. So, we were satisfied with the "same-time" condition.
- It was checking check_in_date and unit_id at Check-3. Control of check_in_date is not enough since customers will stay for a period. Same as above, I added period control with both check-in and check-out dates.
- There was a test error at test_different_guest_same_unit_booking_different_date, fixed it with a small copy to get the date in freeze time.

#### New Feature
- Get Booking: I wanted to add a get booking endpoint to see what record we have. That endpoint has 2 optional parameters. You can check from /docs. I also check db from a DB Manager too, but a new endpoint doesn't hurt.
- Allowing guests to extend their stays: I added a new endpoint(extensions) to extend stay. It basically accepts guest_name and unit_id to identify books, also extra nights to extend. In crud.py, there are new functions such as extend_stay and is_extension_possible.
- Booking Extension History: I added new models, table and crud operations for booking extension history. I thought keeping this data somewhere may help with the data analysis process.
- Added new tests for get booking and booking extension.
## Context

We would like you to help us with a small service that we have for handling bookings. A booking for us simply tells us which guest will be staying in which unit, and when they arrive and the number of nights that guest will be enjoying our amazing suites, comfortable beds, great snac.. apologies - I got distracted. Bookings are at the very core of our business and it's important that we get these right - we want to make sure that guests always get what they paid for, and also trying to ensure that our unit are continually booked and have as few empty nights where no-one stays as possible. A unit is simply a location that can be booked, think like a hotel room or even a house. For the exercise today, we would like you to help us solve an issue we've been having with our example service, as well as implement a new feature to improve the code base. While this is an opportunity for you to showcase your skills, we also want to be respectful of your time and suggest spending no more than 3 hours on this (of course you may also spend longer if you feel that is necessary)

### You should help us:
Identify and fix a bug that we've been having with bookings - there seems to be something going wrong with the booking process where a guest will arrive at a unit only to find that it's already booked and someone else is there!

### Implement a new feature: 
Allowing guests to extend their stays if possible. It happens that <strike>sometimes</strike> all the time people love staying at our locations so much that they want to extend their stay and remain there a while longer. We'd like a new API that will let them do that 

While we provide a choice of projects to work with (either `TS`, `Python`, or `Kotlin`), we understand if you want to implement this in something you're more comfortable with. You are free to re-implement the parts that we have provided in another language, however this may take some time and we would encourage you not spend more time than you're comfortable with!

When implementing, make sure you follow known best practices around architecture, testability, and documentation.


## How to run

### Prerequisutes

Make sure to have the following installed

- Python3
- git
- docker

### Setup

To get started, clone the repository locally and run the following

```shell
[~]$ docker-compose up
Attaching to fastapi-application
fastapi-application  | INFO:     Started server process [1]
fastapi-application  | INFO:     Waiting for application startup.
fastapi-application  | INFO:     Application startup complete.
fastapi-application  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
fastapi-application  | INFO:     192.168.112.1:64034 - "GET / HTTP/1.1" 200 OK
```

To make sure that everything is setup properly, open http://localhost:8000 in your browser and you should see an OK message.
The logs should be looking like this

```shell
fastapi-application  | INFO:     192.168.112.1:64034 - "GET /docs HTTP/1.1" 200 OK
```

To navigate to the swagger docs, open the url http://localhost:8000/docs , the logs should be looking like this

```shell
fastapi-application  | INFO:     192.168.112.1:64034 - "GET /openapi.json HTTP/1.1" 200 OK
```

### Running tests

Open your terminal and run the following commands in the cloned directory (ignore the failing test)

```shell
[~]$ source ./venv/bin/activate  # activate the virtual env shell
(venv)[~]$ pytest

=========================================================================== test session starts ============================================================================
platform darwin -- Python 3.10.9, pytest-7.3.1, pluggy-1.0.0
rootdir: /Users/saifmirza/work/backend-challenge-python
plugins: freezegun-0.4.2, asyncio-0.21.0, anyio-3.6.2
asyncio: mode=strict
collected 5 items                                                                                                                                                          

========================================================================= short test summary info ==========================================================================
FAILED app/test_bookings.py::test_different_guest_same_unit_booking_different_date - AssertionError: {"guest_name":"GuestB","unit_id":"1","check_in_date":"2023-05-22","number_of_nights":5}
================================================================= 1 failed, 4 passed, 21 warnings in 0.36s =================================================================

```


