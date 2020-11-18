from collections import Counter

import pytest

from uobtheatre.bookings.models import (Discount, DiscountCombination,
                                        DiscountRequirement, combinations)
from uobtheatre.bookings.test.factories import (BookingFactory,
                                                ConsessionTypeFactory,
                                                DiscountFactory,
                                                DiscountRequirementFactory,
                                                PerformanceSeatPriceFactory,
                                                SeatBookingFactory)
from uobtheatre.productions.test.factories import PerformanceFactory
from uobtheatre.venues.test.factories import SeatGroupFactory, VenueFactory


@pytest.mark.parametrize(
    "input, length, output",
    [
        (
            [1, 2, 3],
            2,
            [
                (1,),
                (2,),
                (3,),
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
            ],
        ),
        (
            [1, 2, 3],
            3,
            [
                (1,),
                (2,),
                (3,),
                (1, 1),
                (1, 2),
                (1, 3),
                (2, 1),
                (2, 2),
                (2, 3),
                (3, 1),
                (3, 2),
                (3, 3),
                (1, 1, 1),
                (1, 1, 2),
                (1, 1, 3),
                (1, 2, 1),
                (1, 2, 2),
                (1, 2, 3),
                (1, 3, 1),
                (1, 3, 2),
                (1, 3, 3),
                (2, 1, 1),
                (2, 1, 2),
                (2, 1, 3),
                (2, 2, 1),
                (2, 2, 2),
                (2, 2, 3),
                (2, 3, 1),
                (2, 3, 2),
                (2, 3, 3),
                (3, 1, 1),
                (3, 1, 2),
                (3, 1, 3),
                (3, 2, 1),
                (3, 2, 2),
                (3, 2, 3),
                (3, 3, 1),
                (3, 3, 2),
                (3, 3, 3),
            ],
        ),
    ],
)
def test_combinations(input, length, output):
    calculated_combinations = combinations(input, length)
    assert set(calculated_combinations) == set(output)
    assert len(calculated_combinations) == len(output)


@pytest.mark.django_db
def test_is_valid_single_discount():
    booking = BookingFactory()
    discount = DiscountFactory()
    discount.performance = booking.performance

    # Create a discount that requires one student
    consession_type_student = ConsessionTypeFactory(name="Student")
    discount_requirements = DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount
    )

    # When no seats are booked assert this discount cannot be applied
    assert not booking.is_valid_discount_combination(DiscountCombination((discount,)))

    # When one non student seat is booked assert this discount cannot be applied
    seat_booking = SeatBookingFactory(booking=booking)
    assert not booking.is_valid_discount_combination(DiscountCombination((discount,)))

    # When a student seat is booked assert this discount can be applied
    seat_booking = SeatBookingFactory(
        booking=booking, consession_type=consession_type_student
    )
    assert booking.is_valid_discount_combination(DiscountCombination((discount,)))


@pytest.mark.django_db
def test_is_valid_multi_discount():
    booking = BookingFactory()
    discount = DiscountFactory()
    discount.performance = booking.performance

    # Create a discount that requires one student
    consession_type_student = ConsessionTypeFactory(name="Student")
    consession_type_adult = ConsessionTypeFactory(name="Adult")
    discount_requirements = DiscountRequirementFactory(
        consession_type=consession_type_student, number=2, discount=discount
    )
    discount_requirements = DiscountRequirementFactory(
        consession_type=consession_type_adult, number=1, discount=discount
    )

    # When no seats are booked assert this discount cannot be applied
    assert not booking.is_valid_discount_combination(DiscountCombination((discount,)))

    # When only one student seat is booked and two adult seat assert this
    # discount cannot be applied
    SeatBookingFactory(booking=booking, consession_type=consession_type_adult)
    SeatBookingFactory(booking=booking, consession_type=consession_type_adult)
    SeatBookingFactory(booking=booking, consession_type=consession_type_student)
    assert not booking.is_valid_discount_combination(DiscountCombination((discount,)))

    # When a student seat is booked assert this discount can be applied
    SeatBookingFactory(booking=booking, consession_type=consession_type_student)
    assert booking.is_valid_discount_combination(DiscountCombination((discount,)))


@pytest.mark.django_db
def test_get_valid_discounts():
    performance = PerformanceFactory()
    booking = BookingFactory(performance=performance)

    # Create some consession types
    consession_type_student = ConsessionTypeFactory(name="Student")
    consession_type_adult = ConsessionTypeFactory(name="Adult")

    # Create a family discount - 1 student ticket and 2 adults required
    discount_family = DiscountFactory(name="Family", discount=0.2)
    discount_family.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_family
    )
    DiscountRequirementFactory(
        consession_type=consession_type_adult, number=2, discount=discount_family
    )

    # Create a student discount - 1 student ticket required
    discount_student = DiscountFactory(name="Student", discount=0.2)
    discount_student.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_student
    )

    # Check that both discounts have been created
    assert performance.discounts.all().count() == 2

    # When no seats are booked there are no valid discounts
    assert booking.get_valid_discounts() == []

    # When one student seat is booked the student discount should be available
    SeatBookingFactory(booking=booking, consession_type=consession_type_student)
    assert booking.get_valid_discounts() == [DiscountCombination((discount_student,))]

    SeatBookingFactory(booking=booking, consession_type=consession_type_adult)
    SeatBookingFactory(booking=booking, consession_type=consession_type_adult)
    assert set(
        map(lambda d: d.discount_combination, booking.get_valid_discounts())
    ) == set(
        [
            (discount_student,),
            (discount_family,),
        ]
    )

    SeatBookingFactory(booking=booking, consession_type=consession_type_student)
    assert set(
        map(lambda d: d.discount_combination, booking.get_valid_discounts())
    ) == set(
        [
            (discount_family, discount_student),
            (discount_student, discount_family),
            (discount_family,),
            (discount_student,),
            (discount_student, discount_student),
        ]
    )


@pytest.mark.django_db
def test_get_price():
    venue = VenueFactory()
    performance = PerformanceFactory(venue=venue)
    booking = BookingFactory(performance=performance)

    seat_group = SeatGroupFactory(venue=venue)

    # Set seat type price for performance
    seat_price = PerformanceSeatPriceFactory(performance=performance)
    seat_price.seat_group.set([seat_group])

    # Create a seat booking
    SeatBookingFactory(booking=booking, seat_group=seat_group)

    assert booking.get_price() == seat_price.price

    SeatBookingFactory(booking=booking, seat_group=seat_group)
    assert booking.get_price() == seat_price.price * 2

    seat_group_2 = SeatGroupFactory(venue=venue)
    seat_price_2 = PerformanceSeatPriceFactory(performance=performance)
    seat_price_2.seat_group.set([seat_group_2])
    SeatBookingFactory(booking=booking, seat_group=seat_group_2)
    assert booking.get_price() == seat_price.price * 2 + seat_price_2.price


@pytest.mark.skip(reason="This needs implementing")
@pytest.mark.django_db
def test_graceful_response_to_no_price():
    venue = VenueFactory()
    performance = PerformanceFactory(venue=venue)
    booking = BookingFactory(performance=performance)

    seat_group = SeatGroupFactory(venue=venue)

    """ 
    Inorder to set the price of the seat_group the user is about to book we
    would need to use the PerformanceSeatPriceFactory as below:
   
    ```
    seat_price = PerformanceSeatPriceFactory(performance=performance)
    seat_price.seat_group.set([seat_group])
    ```

    If we do not do this no price will be found for the booked seat and bad
    things will happen.

    Most importantly a user should not be able to book a seat if this is the
    case as that means this seat has not been asigned for the show yet...
    """

    # Create a seat booking
    SeatBookingFactory(booking=booking, seat_group=seat_group)
    assert booking.get_price() == seat_price.price


@pytest.mark.django_db
def test_get_price_with_discount():
    venue = VenueFactory()
    performance = PerformanceFactory(venue=venue)
    booking = BookingFactory(performance=performance)

    seat_group = SeatGroupFactory(venue=venue)
    consession_type_student = ConsessionTypeFactory(name="Student")
    consession_type_adult = ConsessionTypeFactory(name="Adult")

    # Set seat type price for performance
    seat_price = PerformanceSeatPriceFactory(performance=performance)
    seat_price.seat_group.set([seat_group])

    # Create a seat booking
    SeatBookingFactory(
        booking=booking, seat_group=seat_group, consession_type=consession_type_student
    )
    SeatBookingFactory(
        booking=booking, seat_group=seat_group, consession_type=consession_type_student
    )

    # Check price without discount
    assert booking.get_price() == seat_price.price * 2

    discount_student = DiscountFactory(name="Student", discount=0.2)
    discount_student.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_student
    )
    discount_combination = DiscountCombination((discount_student,))
    assert discount_student.discount == 0.2
    assert round(booking.get_price_with_discounts(discount_combination)) == round(
        (seat_price.price * (1 - discount_student.discount)) + seat_price.price
    )

    discount_family = DiscountFactory(name="Family", discount=0.2)
    discount_family.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_family
    )
    DiscountRequirementFactory(
        consession_type=consession_type_adult, number=2, discount=discount_family
    )

    SeatBookingFactory(
        booking=booking, seat_group=seat_group, consession_type=consession_type_adult
    )
    SeatBookingFactory(
        booking=booking, seat_group=seat_group, consession_type=consession_type_adult
    )

    discount_combination = DiscountCombination((discount_student, discount_family))
    assert round(booking.get_price_with_discounts(discount_combination)) == round(
        (seat_price.price * (1 - discount_student.discount))
        + (seat_price.price * 3 * (1 - discount_family.discount))
    )


@pytest.mark.django_db
def test_get_best_discount_combination():
    performance = PerformanceFactory()
    booking = BookingFactory(performance=performance)
    venue = VenueFactory()

    # Create some consession types
    consession_type_student = ConsessionTypeFactory(name="Student")
    consession_type_adult = ConsessionTypeFactory(name="Adult")

    seat_group = SeatGroupFactory(venue=venue)

    # Set seat type price for performance
    seat_price = PerformanceSeatPriceFactory(performance=performance)
    seat_price.seat_group.set([seat_group])

    # Create a family discount - 1 student ticket and 2 adults required
    discount_family = DiscountFactory(name="Family", discount=0.2)
    discount_family.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_family
    )
    DiscountRequirementFactory(
        consession_type=consession_type_adult, number=2, discount=discount_family
    )

    # Create a student discount - 1 student ticket required
    discount_student = DiscountFactory(name="Student", discount=0.2)
    discount_student.performances.set([performance])
    DiscountRequirementFactory(
        consession_type=consession_type_student, number=1, discount=discount_student
    )

    SeatBookingFactory(
        booking=booking, consession_type=consession_type_student, seat_group=seat_group
    )
    SeatBookingFactory(
        booking=booking, consession_type=consession_type_adult, seat_group=seat_group
    )
    SeatBookingFactory(
        booking=booking, consession_type=consession_type_adult, seat_group=seat_group
    )
    SeatBookingFactory(
        booking=booking, consession_type=consession_type_student, seat_group=seat_group
    )

    assert booking.performance.discounts.count() == 2

    assert booking.performance.discounts.first().name == "Family"
    assert booking.performance.discounts.first().discount == 0.2
    assert set(booking.get_best_discount_combination().discount_combination) == set(
        (
            discount_student,
            discount_family,
        )
    )
