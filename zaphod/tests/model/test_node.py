from ... import model

from .base import ModelTest


class TestNode(ModelTest):
    @classmethod
    def _setup_once_data(cls):
        node = model.Node(name=u'Test Node',
                          body=u'The quick brown fox...',
                          published=True)
        model.Session.add(node)
        node.aliases.append(model.Alias(path='test-node',
                                        canonical=True))
        node.aliases.append(model.Alias(path='test-node-alias',
                                        canonical=False))

        node.image_metas.append(
            model.ImageMeta(name='test-image-for-node',
                            original_ext='jpg'))

        model.Session.flush()
        cls.node_id = node.id

    # def test_image_normal(self):
    #     node = model.Node.get(self.node_id)
    #     img = node.img(request)
    #     self.assertIn('test-image-for-node', img)
    #     self.assertIn('<img', img)
    #     img = node.img(request, 'tiny')
    #     self.assertIn('test-image-for-node_jpg_tiny.jpg', img)
    #     self.assertIn('<img', img)

    def test_canonical_path(self):
        n = model.Node(name=u'Hello Node')
        with self.assertRaises(AttributeError):
            self.assertIsNone(n.canonical_path())
        n.aliases.append(model.Alias(path='hello-node',
                                     canonical=True))
        self.assertEqual(n.canonical_path(), 'hello-node')

    def test_update_path(self):
        n = model.Node(name=u'Sup Sup')
        n.update_path('sup-sup')
        self.assertEqual(n.canonical_path(), 'sup-sup')

        n.update_path('yo-yo')
        self.assertEqual(n.canonical_path(), 'yo-yo')

    def test_generate_path(self):
        n = model.Node(name=u'Foo Bar')
        self.assertEqual(n.generate_path(), 'foo-bar')

        n.name = u''
        self.assertEqual(n.generate_path(), 'node-none')

        n.id = 99
        self.assertEqual(n.generate_path(), 'node-99')

    def test_override_path(self):
        n = model.Node(name=u'Hello')
        self.assertEqual(n.override_path, None)

        n.override_path = 'blah'
        self.assertEqual(n.override_path, 'blah')

        n.override_path = None
        self.assertEqual(n.override_path, None)
        self.assertEqual(n.canonical_path(), 'hello')
