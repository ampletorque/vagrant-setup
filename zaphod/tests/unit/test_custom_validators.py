from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase
from formencode import Invalid, Schema, validators, NestedVariables

from ... import custom_validators


class TestCustomValidators(TestCase):
    def _run_validator_test(self, validator, value, should_be_valid,
                            state=None):
        try:
            validated = validator.to_python(value, state)
        except Invalid, e:
            if should_be_valid:
                raise AssertionError("'%s' should be valid, got %s" %
                                     (value, e))
        else:
            if should_be_valid is False:
                raise AssertionError("'%s' should be invalid" % value)
            elif should_be_valid is not True:
                self.assertEqual(should_be_valid, validated)

    def test_urlstring_bad_chars(self):
        self._run_validator_test(custom_validators.URLString(),
                                 "Invalid URL String", False)

    def test_urlstring_good_chars(self):
        self._run_validator_test(custom_validators.URLString(),
                                 "valid-url-string", True)

    def test_clonefields_simple(self):
        class TestSchema(Schema):
            pre_validators = [custom_validators.CloneFields('from_fields',
                                                            'to_fields',
                                                            when='selector')]
            from_fields = validators.String()
            to_fields = validators.String()
            selector = validators.Bool()

        ts = TestSchema()
        self.assertEqual(
            ts.to_python({'from_fields': 'foo',
                          'to_fields': 'bar',
                          'selector': '1'}),
            {'from_fields': 'foo',
             'to_fields': 'foo',
             'selector': True})
        self.assertEqual(
            ts.to_python({'from_fields': 'foo',
                          'to_fields': 'bar'}),
            {'from_fields': 'foo',
             'to_fields': 'bar',
             'selector': False})

    def test_clonefields_compound(self):
        class SubSchema(Schema):
            a = validators.String()
            b = validators.Int()

        class TestSchema(Schema):
            pre_validators = [NestedVariables(),
                              custom_validators.CloneFields('pumpkin',
                                                            'pie',
                                                            when='thankful')]
            pumpkin = SubSchema()
            pie = SubSchema()
            thankful = validators.Bool()

        ts = TestSchema()
        self.assertEqual(ts.to_python({'pumpkin.a': 'hello',
                                       'pumpkin.b': '123',
                                       'pie.a': 'world',
                                       'pie.b': '200'}),
                         {'pumpkin': {'a': 'hello',
                                      'b': 123},
                          'pie': {'a': 'world',
                                  'b': 200},
                          'thankful': False})

        self.assertEqual(ts.to_python({'pumpkin.a': 'hello',
                                       'pumpkin.b': '123',
                                       'pie.a': 'world',
                                       'pie.b': '200',
                                       'thankful': '1'}),
                         {'pumpkin': {'a': 'hello',
                                      'b': 123},
                          'pie': {'a': 'hello',
                                  'b': 123},
                          'thankful': True})

    def test_select_validator(self):
        class SchemaA(Schema):
            field = validators.Int()

        class SchemaB(Schema):
            field = validators.Number()

        class SchemaDefault(Schema):
            field = validators.String()

        class TestSchema(Schema):
            pre_validators = [NestedVariables()]
            val = custom_validators.SelectValidator(
                {'a': SchemaA(),
                 'b': SchemaB()},
                SchemaDefault())

        ts = TestSchema()
        self.assertEqual(ts.to_python({'val.selector': 'a',
                                       'val.field': '123'}),
                         {'val': {'field': 123}})
        with self.assertRaises(Invalid):
            ts.to_python({'val.selector': 'a',
                          'val.field': '12.3'})

        self.assertEqual(ts.to_python({'val.selector': 'b',
                                       'val.field': '123'}),
                         {'val': {'field': 123}})
        with self.assertRaises(Invalid):
            ts.to_python({'val.selector': 'b',
                          'val.field': 'foo'})

        self.assertEqual(ts.to_python({'val.selector': 'blah',
                                       'val.field': '123'}),
                         {'val': {'field': '123'}})
        self.assertEqual(ts.to_python({'val.selector': 'blah',
                                       'val.field': 'foo'}),
                         {'val': {'field': 'foo'}})

        # No selector field should make default validator used.
        self.assertEqual(ts.to_python({'val.field': '123'}),
                         {'val': {'field': '123'}})

    def test_wildcard_schema(self):
        v = custom_validators.WildcardSchema()
        self.assertEqual(v.to_python({1: 'quux', 'hello': 3.14}),
                         {1: 'quux', 'hello': 3.14})

    def test_better_phone_validator_good(self):
        v = custom_validators.BetterUSPhoneNumber()
        cases = [
            '888-867-5309',
            '888 867 5309',
            '(888) 867-5309',
            '(888)8675309',
            '8888675309',
            '888.867.5309',
            '+1 (888) 867-5309',
            '1.888.867.5309',
            '1-888-867-5309',
        ]

        for case in cases:
            self.assertEqual(v.to_python(case), '888-867-5309')

        for case in ['1-123-867-5309',
                     '+1 (123) 867-5309',
                     '123-867-5309',
                     '(123) 867-5309']:
            self.assertEqual(v.to_python(case), '123-867-5309')

    def test_better_phone_validator_bad(self):
        v = custom_validators.BetterUSPhoneNumber()
        bad_cases = [
            '5-888-867-5309',
            '88-867-5309',
            '88 867 5309',
            '38888675309',
            # FIXME This is a case that we'd kind of like to be able to fix,
            # but can't flag it yet because it reformats to 188-867-5309
            # '1-88-867-5309',
            '0-888-867-530',
        ]
        for bad_case in bad_cases:
            print("checking %r" % bad_case)
            with self.assertRaises(Invalid) as cm:
                v.to_python(bad_case)
            self.assertIn('10 digits', str(cm.exception))
