import unittest
from routing_regression_prototype import propose_intent

class RoutingPrototypeTests(unittest.TestCase):
    def test_tracking_paraphrase_candidate_only(self):
        x = propose_intent("Can you track my parcel?")
        self.assertEqual(x["route"], "candidate_order_lookup")
        self.assertEqual(x["reason"], "requires_account_verification")

    def test_exchange_paraphrase_candidate_only(self):
        x = propose_intent("Could I swap the size of my item?")
        self.assertEqual(x["route"], "candidate_exchange")

    def test_mixed_intent_abstains(self):
        x = propose_intent("Track my package and exchange the size of my item")
        self.assertEqual(x["route"], "clarify")

    def test_human_request_precedes_other_routes(self):
        x = propose_intent("Please connect me to a human to track my order")
        self.assertEqual(x["route"], "human")

    def test_sensitive_request_handoff(self):
        x = propose_intent("My account locked, where is my parcel?")
        self.assertEqual(x["route"], "human")

    def test_no_guess_from_generic_status(self):
        self.assertEqual(propose_intent("What is my status?")["route"], "clarify")

    def test_invalid_input(self):
        self.assertEqual(propose_intent("x"*2001)["route"], "clarify")

if __name__ == "__main__":
    unittest.main()
