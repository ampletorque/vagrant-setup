from . import FunctionalBase


class TestBrowse(FunctionalBase):

    def test_browse(self):
        resp = self.app.get('/browse')
        body = resp.body.decode('utf-8')
        self.assertIn('Lifestyle', body)
        self.assertNotIn('Unlisted Tag', body)
