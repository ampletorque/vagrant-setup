from . import FunctionalBase


class TestIndex(FunctionalBase):

    def test_index(self):
        resp = self.app.get('/')
        resp.mustcontain('Recently')
