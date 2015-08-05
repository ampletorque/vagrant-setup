from sqlalchemy import Column, types
from sqlalchemy.orm import composite
from sqlalchemy.ext.mutable import MutableComposite

from iso3166 import countries

__all__ = ['Address']


def make_address_columns(name):
    """
    Returns a sqlalchemy composite column object which can persist an Address
    object in a declaratively mapped class.
    """
    cols = [Column('%s_%s' % (name, col),
                   types.Unicode(255), nullable=False, default=u'')
            for col in Address.column_ordering]
    return composite(Address, *cols)


class Address(MutableComposite):
    """
    An address object which can be used for shipping, as a compound type in
    SQLAlchemy, etc.
    """
    column_ordering = ['first_name',
                       'last_name',
                       'company',
                       'phone',
                       'address1',
                       'address2',
                       'city',
                       'state',
                       'postal_code',
                       'country_code']

    def __init__(self,
                 first_name=u'',
                 last_name=u'',
                 company=u'',
                 phone=u'',
                 address1=u'',
                 address2=u'',
                 city=u'',
                 state=u'',
                 postal_code=u'',
                 country_code=u''):
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.phone = phone
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country_code = country_code

    def __composite_values__(self):
        return (self.first_name, self.last_name, self.company,
                self.phone, self.address1, self.address2, self.city,
                self.state, self.postal_code, self.country_code)

    def __getstate__(self):
        return self.__composite_values__()

    def __setstate__(self, state):
        (self.first_name, self.last_name, self.company,
         self.phone, self.address1, self.address2, self.city,
         self.state, self.postal_code, self.country_code) = state

    def __setattr__(self, key, value):
        # Track changes to attributes so that we can tell the SQLAlchemy
        # session that this composite column has changed, and it should be
        # persisted.
        object.__setattr__(self, key, value)
        self.changed()

    def __eq__(self, other):
        return (isinstance(other, Address) and
                all((getattr(self, c) == getattr(other, c)
                     for c in self.column_ordering)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ("<Address(" +
                " ".join("%s=%s" % (k, v) for k, v in self) +
                ")>")

    def __iter__(self):
        return ((c, getattr(self, c)) for c in self.column_ordering)

    @property
    def country_name(self):
        """
        Full name of the country for this address. An 'apolitical' name, chosen
        to avoid controversy, is used instead of the exact ISO3166 name.
        """
        lookup = {c.alpha2.lower(): c.name for c in countries}
        return lookup.get(self.country_code, self.country_code)

    @property
    def full_name(self):
        """
        Full name of addressee (first and last names concatenated).
        """
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def inline(self):
        """
        A single-line representation of this address.
        """
        s = ''
        if self.address1:
            s += self.address1 + ', '
        if self.address2:
            s += self.address2 + ', '
        if self.city:
            s += self.city + ', '
        if self.state:
            s += self.state + ' ' + self.postal_code + ', '
        if self.country_code:
            s += self.country_code.upper()
        return s

    def to_json(self):
        return {col: getattr(self, col) for col in self.column_ordering}
