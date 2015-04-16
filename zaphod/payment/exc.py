"""
Common payment handling exceptions. Use these rather than implementing new
ones.
"""
class PaymentException(Exception):
    message = "A payment error occurred."

    def __str__(self):
        m = Exception.__str__(self)
        return self.message if not m else "%s: %s" % (self.message, m)


class UnknownGatewayException(PaymentException):
    message = "Unknown payment gateway."


class ProfileNotFoundException(PaymentException):
    message = "Payment profile not found."


class TransactionNotFoundException(PaymentException):
    message = "Transaction not found."


class ProfileException(PaymentException):
    message = "A payment profile error occurred."


class InvalidProfileIDException(ProfileException):
    message = "Invalid profile ID specified."


class ProcessingErrorException(ProfileException):
    message = "A processing error occured."


class TransactionDeclinedException(PaymentException):
    message = "Transaction was declined."


class DuplicateTransactionException(PaymentException):
    message = "Duplication transaction detected."


class AuthenticationException(PaymentException):
    message = "A payment gateway authentication error occurred."


class InvalidCardNumberException(PaymentException):
    message = "Invalid card number."


class InvalidExpirationException(PaymentException):
    message = "Invalid expiration date."


class InvalidAmountException(PaymentException):
    message = "Invalid transaction amount."


class ExpiredCardException(PaymentException):
    message = "Card has expired."


class CardTypeNotAcceptedException(PaymentException):
    message = "Card type not accepted."


class AVSMismatchException(PaymentException):
    message = "AVS Mismatch: Billing address does not match address on file."


class CannotCreditException(PaymentException):
    message = "Cannot create payment credit."


class ParameterException(PaymentException):
    message = "Parameter error."
