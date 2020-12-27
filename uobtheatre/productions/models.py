import math
import uuid
from typing import List

from autoslug import AutoSlugField
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.functional import cached_property

from uobtheatre.societies.models import Society
from uobtheatre.utils.models import TimeStampedMixin
from uobtheatre.venues.models import SeatGroup, Venue


class CrewRole(models.Model):
    """Crew role"""

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Warning(models.Model):
    """A venue is a space often where shows take place"""

    warning = models.CharField(max_length=255)

    def __str__(self):
        return self.warning


class Production(models.Model, TimeStampedMixin):
    """A production is a show (like the 2 weeks things) and can have many
    performaces (these are like the nights).
    """

    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)

    society = models.ForeignKey(Society, on_delete=models.SET_NULL, null=True)

    poster_image = models.ImageField(null=True)
    featured_image = models.ImageField(null=True)
    cover_image = models.ImageField(null=True)

    age_rating = models.SmallIntegerField(null=True)
    facebook_event = models.CharField(max_length=255, null=True)

    warnings = models.ManyToManyField(Warning)

    slug = AutoSlugField(populate_from="name", unique=True, blank=True)

    def __str__(self):
        return self.name

    def is_upcoming(self) -> bool:
        """
        Returns if the show is upcoming. If the show has no upcoming
        productions (not ended) then it is not upcoming.
        """
        performances = self.performances.all()
        return any(performance.start > timezone.now() for performance in performances)

    def end_date(self):
        """
        Return when the last performance ends.
        """
        performances = self.performances.all()
        if not performances:
            return None
        return max(performance.end for performance in performances)

    def start_date(self):
        """
        Return when the first performance starts.
        """
        performances = self.performances.all()
        if not performances:
            return None
        return min(performance.start for performance in performances)

    def duration(self):
        """
        Returns the duration of the shortest show as a datetime object.
        """
        performances = self.performances.all()
        if not performances:
            return None
        return min(performance.duration() for performance in performances)


class CastMember(models.Model):
    """Member of production cast"""

    name = models.CharField(max_length=255)
    profile_picture = models.ImageField(null=True, blank=True)
    role = models.CharField(max_length=255, null=True)
    production = models.ForeignKey(
        Production, on_delete=models.CASCADE, related_name="cast"
    )

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    """Member of production crew"""

    name = models.CharField(max_length=255)
    role = models.ForeignKey(CrewRole, null=True, on_delete=models.SET_NULL)
    production = models.ForeignKey(
        Production, on_delete=models.CASCADE, related_name="crew"
    )

    def __str__(self):
        return self.name


class Performance(models.Model, TimeStampedMixin):
    """
    A performance is a discrete event when the show takes place eg 7pm on
    Tuesday.
    """

    production = models.ForeignKey(
        Production, on_delete=models.CASCADE, related_name="performances"
    )

    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    extra_information = models.TextField(null=True, blank=True)

    seat_groups = models.ManyToManyField(SeatGroup, through="PerformanceSeatGroup")

    def tickets(self, seat_group=None):
        """ Get all tickets for this performance """
        filters = {}
        if seat_group:
            filters["seat_group"] = seat_group

        return [
            ticket
            for booking in self.bookings.all()
            for ticket in booking.tickets.filter(**filters)
        ]

    def total_capacity(self, seat_group=None):
        """ Returns the total capacity of show. """
        if seat_group:
            queryset = self.performance_seat_groups
            try:
                return queryset.get(seat_group=seat_group).capacity
            except queryset.model.DoesNotExist:
                print("NOT FOUND")
                return 0
        response = self.performance_seat_groups.aggregate(Sum("capacity"))
        return response["capacity__sum"] or 0

    def capacity_remaining(self, seat_group: SeatGroup = None):
        """ Returns the capacity remaining.  """
        # self.select_related("bookings").prefetch_related("seat_bookings").filter(
        #     seat_group=seat_group
        # ).count()
        if seat_group:
            self.total_capacity(seat_group=seat_group) - self.seats_booked()
        return sum(
            self.capacity_remaining(seat_group=seating.seat_group)
            for seating in self.seating.all()
        )

    def seat_group_capacity(self, seat_group: SeatGroup):
        """
        Given a seat group, returns the capacity of that seat group for this
        performance.
        """
        return self.seating.get(seat_group=seat_group).capacity

    def duration(self):
        """
        Returns the duration of the show as a datetime object
        """
        return self.end - self.start

    def get_single_discounts(self):
        """ Returns all discounts that apply to a single ticket """
        return [
            discount
            for discount in self.discounts.all()
            if discount.is_single_discount()
        ]

    def get_conession_discount(self, consession_type) -> float:
        """
        Given a seat_group and a consession type returns the consession type
        discount for the ticket.
        """
        discount = next(
            (
                discount
                for discount in self.get_single_discounts()
                if discount.discount_requirements.first().consession_type
                == consession_type
            ),
            None,
        )
        return discount.discount if discount else 0

    def price_with_consession(self, consession, price) -> int:
        """
        Given a seat_group and a consession type returns the price of the
        ticket with the single discounts applied.
        """
        return math.ceil((1 - self.get_conession_discount(consession)) * price)

    def consessions(self) -> List:
        """ Returns list of all consession types """
        consession_list = list(
            set(
                discounts_requirement.consession_type
                for discount in self.discounts.all()
                for discounts_requirement in discount.discount_requirements.all()
            )
        )
        consession_list.sort(key=lambda consession: consession.id)
        return consession_list

    def __str__(self):
        if self.start is None:
            return f"Perforamce of {self.production.name}"
        return f"Perforamce of {self.production.name} at {self.start.strftime('%H:%M')} on {self.start.strftime('%m/%d/%Y')}"


class PerformanceSeatGroup(models.Model):
    """ Storing the price and number of seats of each seat group for a show """

    seat_group = models.ForeignKey(SeatGroup, on_delete=models.RESTRICT)
    performance = models.ForeignKey(
        Performance, on_delete=models.RESTRICT, related_name="performance_seat_groups"
    )
    price = models.IntegerField()
    capacity = models.SmallIntegerField(blank=True)

    def total_seat_bookings(self, seat_group=None):
        if seat_group:
            self.seat_bookings.all()

    def capacity_remaining(self):
        self.capacity - self.total_seat_bookings()
