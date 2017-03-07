import unittest

from http_prompt.tree import Node, TreeTraveler


class TestNode(unittest.TestCase):

    def setUp(self):
        # Make a tree like this:
        #         root
        #     a             h
        #  b     d        i   n
        # c f   e g     k     o
        #             l m p
        self.root = Node('root')
        self.root.add_path('a', 'b', 'c')
        self.root.add_path('a', 'b', 'f')
        self.root.add_path('a', 'd', 'e')
        self.root.add_path('a', 'd', 'g')
        self.root.add_path('h', 'i', 'k', 'l')
        self.root.add_path('h', 'i', 'k', 'm')
        self.root.add_path('h', 'i', 'k', 'p')
        self.root.add_path('h', 'n', 'o')

    def test_illegal_name(self):
        self.assertRaises(ValueError, Node, '.')
        self.assertRaises(ValueError, Node, '..')

    def test_str(self):
        node = Node('my node')
        self.assertEqual(str(node), 'my node')

    def test_add_path_and_find_child(self):
        # Level 1 (root)
        self.assertEqual(set(c.name for c in self.root.children), set('ah'))

        # Level 2
        node_a = self.root.find_child('a')
        node_h = self.root.find_child('h')
        self.assertEqual(set(c.name for c in node_a.children), set('bd'))
        self.assertEqual(set(c.name for c in node_h.children), set('in'))

        # Level 3
        node_b = node_a.find_child('b')
        node_i = node_h.find_child('i')
        self.assertEqual(set(c.name for c in node_b.children), set('cf'))
        self.assertEqual(set(c.name for c in node_i.children), set('k'))

        # Level 4
        node_c = node_b.find_child('c')
        node_k = node_i.find_child('k')
        self.assertEqual(set(c.name for c in node_c.children), set())
        self.assertEqual(set(c.name for c in node_k.children), set('lmp'))

        # Return None if child can't be found
        self.assertFalse(node_c.find_child('x'))


class TestTreeTraveler(unittest.TestCase):

    def setUp(self):
        # Make a tree like this:
        #         root
        #     a             h
        #  b     d        i   n
        # c f   e g     k     o
        #             l m p
        root = Node('root')
        root.add_path('a', 'b', 'c')
        root.add_path('a', 'b', 'f')
        root.add_path('a', 'd', 'e')
        root.add_path('a', 'd', 'g')
        root.add_path('h', 'i', 'k', 'l')
        root.add_path('h', 'i', 'k', 'm')
        root.add_path('h', 'i', 'k', 'p')
        root.add_path('h', 'n', 'o')

        self.traveler = TreeTraveler(root)

    def test_initial_state(self):
        self.assertEqual(self.traveler.root.name, 'root')
        self.assertEqual(self.traveler.cur.name, 'root')

    def test_goto_relative(self):
        self.assertTrue(self.traveler.goto('a'))
        self.assertEqual(self.traveler.cur.name, 'a')

        self.assertTrue(self.traveler.goto('b/f'))
        self.assertEqual(self.traveler.cur.name, 'f')

    def test_goto_root(self):
        self.assertTrue(self.traveler.goto('a/b/c'))
        self.assertEqual(self.traveler.cur.name, 'c')

        self.assertTrue(self.traveler.goto('/'))
        self.assertEqual(self.traveler.cur.name, 'root')

    def test_goto_non_existing(self):
        self.assertFalse(self.traveler.goto('x'))
        self.assertEqual(self.traveler.cur.name, 'root')

        self.assertFalse(self.traveler.goto('a/b/x'))
        self.assertEqual(self.traveler.cur.name, 'root')

    def test_goto_absolute(self):
        self.assertTrue(self.traveler.goto('a/b/c'))
        self.assertEqual(self.traveler.cur.name, 'c')

        self.assertFalse(self.traveler.goto('h/i'))
        self.assertEqual(self.traveler.cur.name, 'c')

        self.assertTrue(self.traveler.goto('/h/i'))
        self.assertEqual(self.traveler.cur.name, 'i')

    def test_goto_extra_slashes(self):
        self.assertTrue(self.traveler.goto('a/b/c/'))
        self.assertEqual(self.traveler.cur.name, 'c')

        self.assertTrue(self.traveler.goto('/////h//////i//////'))
        self.assertEqual(self.traveler.cur.name, 'i')

    def test_goto_parent(self):
        self.assertTrue(self.traveler.goto('h/i/k/l'))
        self.assertEqual(self.traveler.cur.name, 'l')

        self.assertTrue(self.traveler.goto('..'))
        self.assertEqual(self.traveler.cur.name, 'k')

        self.assertTrue(self.traveler.goto('../../n/o'))
        self.assertEqual(self.traveler.cur.name, 'o')

        self.assertTrue(self.traveler.goto('../../////i/k/../../../a'))
        self.assertEqual(self.traveler.cur.name, 'a')

    def test_goto_parent_to_root(self):
        self.assertTrue(self.traveler.goto('../../../../..'))
        self.assertEqual(self.traveler.cur.name, 'root')

        self.assertTrue(self.traveler.goto('a/b'))
        self.assertEqual(self.traveler.cur.name, 'b')

        self.assertTrue(self.traveler.goto('../../../../..'))
        self.assertEqual(self.traveler.cur.name, 'root')

        self.assertTrue(self.traveler.goto('/../../../../a/b'))
        self.assertEqual(self.traveler.cur.name, 'b')

    def test_goto_dot(self):
        self.assertTrue(self.traveler.goto('.'))
        self.assertEqual(self.traveler.cur.name, 'root')

        self.assertTrue(self.traveler.goto('./a/b'))
        self.assertEqual(self.traveler.cur.name, 'b')

        self.assertTrue(self.traveler.goto('./c'))
        self.assertEqual(self.traveler.cur.name, 'c')

        self.assertTrue(self.traveler.goto('./././.'))
        self.assertEqual(self.traveler.cur.name, 'c')
