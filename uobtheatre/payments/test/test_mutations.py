import pytest
from graphql_relay.node.node import to_global_id

from uobtheatre.bookings.test.factories import BookingFactory
from uobtheatre.payments.models import Payment
from uobtheatre.payments.payment_methods import SquareOnline, SquarePOS
from uobtheatre.payments.test.factories import PaymentFactory


@pytest.mark.django_db
def test_cancel_payment_completed_payment(gql_client):
    gql_client.login()
    booking = BookingFactory(creator=gql_client.user)
    payment = PaymentFactory(
        pay_object=booking,
        status=Payment.PaymentStatus.COMPLETED,
        provider=SquarePOS.name,
    )

    response = gql_client.execute(
        """
        mutation {
          cancelPayment(paymentId: "%s") {
            success
            errors {
                __typename
                ... on NonFieldError {
                    message
                    code
                }
            }
          }
        }
        """
        % to_global_id("PaymentNode", payment.id)
    )

    assert response["data"]["cancelPayment"]["errors"] == [
        {
            "__typename": "NonFieldError",
            "message": "A payment must be in progress to be canceled.",
            "code": "400",
        }
    ]


@pytest.mark.django_db
def test_cancel_payment_success(gql_client, mock_square):
    gql_client.login()
    booking = BookingFactory(creator=gql_client.user)
    payment = PaymentFactory(
        pay_object=booking,
        status=Payment.PaymentStatus.PENDING,
        provider=SquarePOS.name,
    )

    with mock_square(
        SquarePOS.client.terminal,
        "cancel_terminal_checkout",
        body={},
        status_code=200,
        success=True,
    ):
        response = gql_client.execute(
            """
            mutation {
              cancelPayment(paymentId: "%s") {
                success
                errors {
                    __typename
                    ... on NonFieldError {
                        message
                        code
                    }
                }
              }
            }
            """
            % to_global_id("PaymentNode", payment.id)
        )

    print(response)
    assert response["data"]["cancelPayment"]["success"]
    assert not response["data"]["cancelPayment"]["errors"]


@pytest.mark.django_db
def test_cancel_payment_not_creator_of_booking(gql_client):
    gql_client.login()
    booking = BookingFactory()
    payment = PaymentFactory(
        pay_object=booking,
        status=Payment.PaymentStatus.PENDING,
        provider=SquarePOS.name,
    )

    response = gql_client.execute(
        """
        mutation {
          cancelPayment(paymentId: "%s") {
            success
            errors {
                __typename
                ... on NonFieldError {
                    message
                    code
                }
            }
          }
        }
        """
        % to_global_id("PaymentNode", payment.id)
    )

    assert response["data"]["cancelPayment"]["errors"] == [
        {
            "__typename": "NonFieldError",
            "message": "You do not have permission to cancel this payment.",
            "code": "403",
        }
    ]


@pytest.mark.django_db
def test_cancel_payment_not_squarepos(gql_client):
    gql_client.login()
    booking = BookingFactory(creator=gql_client.user)
    payment = PaymentFactory(
        pay_object=booking,
        provider=SquareOnline.name,
        status=Payment.PaymentStatus.PENDING,
    )

    response = gql_client.execute(
        """
        mutation {
          cancelPayment(paymentId: "%s") {
            success
            errors {
                __typename
                ... on NonFieldError {
                    message
                    code
                }
            }
          }
        }
        """
        % to_global_id("PaymentNode", payment.id)
    )

    assert response["data"]["cancelPayment"]["errors"] == [
        {
            "__typename": "NonFieldError",
            "message": "This payment method cannot be canceled.",
            "code": "400",
        }
    ]
