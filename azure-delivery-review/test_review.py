import unittest
from review import review

class ReviewTests(unittest.TestCase):
    def test_empty_flags_all(self):
        self.assertTrue(all(x['status'] == 'needs review' for x in review({})))

    def test_only_boolean_true_is_declared(self):
        result = review({'terraform_validation': 'true', 'plan_review': True})
        self.assertEqual(result[0]['status'], 'needs review')
        self.assertEqual(result[1]['status'], 'declared')

    def test_requires_object(self):
        with self.assertRaises(ValueError):
            review([])

if __name__ == '__main__':
    unittest.main()
