"""
주문 관련 예외 처리.
"""


class OrderInvalidProductException(Exception):
    message = "Invalid product ID"


class OrderNotFoundException(Exception):
    message = "Order Not Found"
