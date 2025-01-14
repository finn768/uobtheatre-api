"""
Defines base schema for api
"""

import graphene

import uobtheatre.bookings.mutations as bookings_mutations
import uobtheatre.bookings.schema as bookings_schema
import uobtheatre.discounts.schema as discounts_schema
import uobtheatre.finance.mutations as finance_mutations
import uobtheatre.images.schema as image_schema
import uobtheatre.payments.mutations as payments_mutations
import uobtheatre.payments.schema as payments_schema
import uobtheatre.productions.mutations as productions_mutations
import uobtheatre.productions.schema as productions_schema
import uobtheatre.reports.schema as reports_schema
import uobtheatre.site_messages.mutations as site_messages_mutations
import uobtheatre.site_messages.schema as site_messages_schema
import uobtheatre.societies.schema as societies_schema
import uobtheatre.users.schema as users_schema
import uobtheatre.venues.schema as venues_schema


class Query(
    venues_schema.Query,
    productions_schema.Query,
    societies_schema.Query,
    users_schema.Query,
    bookings_schema.Query,
    payments_schema.Query,
    image_schema.Query,
    site_messages_schema.Query,
    graphene.ObjectType,
):
    """
    Defines base Query for api
    """


class Mutation(
    users_schema.Mutation,
    bookings_mutations.Mutation,
    reports_schema.Mutation,
    payments_mutations.Mutation,
    productions_mutations.Mutation,
    discounts_schema.Mutation,
    finance_mutations.Mutation,
    site_messages_mutations.Mutation,
    graphene.ObjectType,
):
    """
    Defines base Mutation for api
    """


schema = graphene.Schema(query=Query, mutation=Mutation)
