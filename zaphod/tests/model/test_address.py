from unittest import TestCase

import pickle

from ... import model


sample = dict(
    first_name=u'Scott',
    last_name=u'Torborg',
    company=u'Widgets International',
    phone=u'555-555-1212',
    address1=u'123 Main St',
    address2=u'Suite A',
    city=u'Mountain View',
    state=u'CA',
    postal_code=u'94040',
    country_code=u'us')


class TestAddress(TestCase):
    def setUp(self):
        self.a = model.Address(**sample)

        self.b = model.Address(
            first_name='John',
            last_name='Smith',
            company='Apple',
            phone='555-867-5309',
            address1='1 Infinite Loop',
            address2='',
            city='Cupertino',
            state='CA',
            postal_code='95015',
            country_code='us')

        self.c = model.Address(
            first_name='Scott',
            last_name='Torborg',
            company='Widgets International',
            phone='555-555-1212',
            address1='123 Main St',
            address2='',
            city='Mountain View',
            state='CA',
            postal_code='94040',
            country_code='us')

    def test_address_notequal(self):
        self.assertNotEqual(self.a, self.b)

    def test_address_notequal2(self):
        self.c.address2 = ''
        self.assertNotEqual(self.a, self.c)

    def test_address_equal(self):
        self.c.address2 = 'Suite A'
        self.assertEqual(self.a, self.c)

    def test_address_notnone(self):
        self.assertNotEqual(self.a, None)

    def test_address_notother(self):
        self.assertNotEqual(self.a, 'blah')

    def test_address_str(self):
        self.assertTrue(str(self.a).startswith('<Address'))

    def test_address_country_name(self):
        self.assertEqual(self.c.country_name, u'United States')

    def test_unpersisted_pickleable(self):
        s = pickle.dumps(self.a)
        addr2 = pickle.loads(s)
        self.assertEqual(self.a, addr2)

    def test_address_fullname(self):
        self.assertEqual(self.c.full_name, 'Scott Torborg')
