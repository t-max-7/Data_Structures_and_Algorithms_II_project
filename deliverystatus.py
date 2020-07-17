from enum import Enum


# Enum for storing the delivery status for packages
class DeliveryStatus(Enum):
    NOT_AT_DEPOT = 'not at depot'
    AT_DEPOT = 'at depot'
    IN_ROUTE = 'in route'
    DELIVERED = 'delivered'
