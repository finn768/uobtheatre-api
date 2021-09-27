import abc

from uobtheatre.utils.models import AbstractModelMeta


class Payable(metaclass=AbstractModelMeta):
    """
    An model which can be paid for
    """

    @property
    @abc.abstractmethod
    def payment_reference_id(self):
        """
        The id of the payable object provided to payment providers.
        """
        raise NotImplementedError