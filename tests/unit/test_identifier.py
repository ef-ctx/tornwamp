import unittest
from mock import patch

from tornwamp import identifier


class IdentifierTestCase(unittest.TestCase):

    def setUp(self):
        identifier.existing_ids = []

    def tearDown(self):
        identifier.existing_ids = []

    @patch("tornwamp.identifier.random.randint", return_value=10)
    def test_create_global_id(self, randint):
        self.assertEqual(identifier.existing_ids, [])
        new_id = identifier.create_global_id()
        self.assertEqual(new_id, 10)
        self.assertEqual(identifier.existing_ids, [10])
        self.assertEqual(randint.call_count, 1)

    @patch("tornwamp.identifier.random.randint", side_effect=[1105184, 604950])
    def test_create_global_id_random_hit(self, randint):
        identifier.existing_ids = [1105184]
        new_id = identifier.create_global_id()
        self.assertEqual(new_id, 604950)
        self.assertEqual(identifier.existing_ids, [1105184, 604950])
        self.assertEqual(randint.call_count, 2)
