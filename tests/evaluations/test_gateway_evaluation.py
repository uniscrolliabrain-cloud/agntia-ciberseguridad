import unittest
from .runner import evaluate

class EvaluationTests(unittest.TestCase):
    def test_configuration_change_invalidates_results_and_benign_utility_is_required(self):
        cases=[{'id':'benign','label':'benign','mutation':'read','language':'es'}, {'id':'attack','label':'adversarial','mutation':'role','language':'en'}]
        report=evaluate(cases)
        self.assertEqual(report['metrics']['benign_completed'],1)
        self.assertEqual(report['metrics']['false_negatives'],0)
        with self.assertRaises(ValueError):evaluate(cases,expected_configuration='f'*64)
        with self.assertRaises(ValueError):evaluate(cases[1:])
