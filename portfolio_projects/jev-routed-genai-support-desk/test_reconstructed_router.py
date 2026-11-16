import unittest

from reconstructed_router import guard_draft, route_ticket


class RouterTests(unittest.TestCase):
    def test_tracking_paraphrases_without_account_ownership_withhold(self):
        for text in ("Track my package", "Where is my parcel?", "Any order status update?"):
            with self.subTest(text=text):
                result = route_ticket(text)
                self.assertEqual(result.route, "clarify")
                self.assertEqual(result.reason, "order_ownership_unverified")

    def test_tracking_with_synthetic_flag_remains_unsent(self):
        r = route_ticket("Track my package", order_verified=True)
        self.assertEqual(r.route, "read_only_order_lookup")
        self.assertFalse(r.release_authorized)

    def test_exchange_paraphrases_demand_both_sources(self):
        for text in ("Could I swap the size of my item?",
                     "I want to exchange my shirt color"):
            with self.subTest(text=text):
                self.assertEqual(route_ticket(text).reason, "exchange_evidence_missing")
                r = route_ticket(text, order_verified=True, exchange_policy_verified=True)
                self.assertEqual(r.route, "agent_review")
                self.assertFalse(r.release_authorized)

    def test_mixed_intent_abstains(self):
        r = route_ticket("Track my order and exchange my item", order_verified=True)
        self.assertEqual(r.reason, "mixed_intent")

    def test_human_and_sensitive_override_other_routes(self):
        for text in ("Get me a human to track my order",
                     "My card was stolen, can you track my parcel?"):
            self.assertEqual(route_ticket(text).route, "human")

    def test_refund_never_auto_authorized(self):
        r = route_ticket("I want a refund", order_verified=True)
        self.assertEqual(r.route, "human")
        self.assertFalse(r.release_authorized)

    def test_invalid_flag_fails_closed(self):
        self.assertEqual(route_ticket("track my package", order_verified="yes").route, "human")

    def test_draft_guard_holds_unsupported_promise(self):
        r = guard_draft("Your refund is guaranteed", source_ids=["p1"], approved_ids={"p1"})
        self.assertEqual(r.route, "hold")

    def test_draft_guard_holds_wrong_or_duplicate_source(self):
        self.assertEqual(guard_draft("A draft", source_ids=["unapproved"], approved_ids={"p1"}).route, "hold")
        self.assertEqual(guard_draft("A draft", source_ids=["p1", "p1"], approved_ids={"p1"}).route, "hold")

    def test_screened_draft_not_auto_sent(self):
        r = guard_draft("Return policies require review.", source_ids=["p1"], approved_ids={"p1"})
        self.assertEqual(r.route, "agent_review")
        self.assertFalse(r.release_authorized)


if __name__ == "__main__":
    unittest.main()
