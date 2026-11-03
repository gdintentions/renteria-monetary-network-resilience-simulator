"""Optional pqcrypto tests, skipped in standard-library CI when dependency absent."""
import importlib.util
import unittest

@unittest.skipUnless(importlib.util.find_spec("pqcrypto"),"Optional pqcrypto not installed")
class PQCTests(unittest.TestCase):
    def test_local_ml_kem_and_ml_dsa(self):
        from scripts.run_pqc import run
        output=run()
        self.assertTrue(output["shared_secret_matches"])
        self.assertTrue(output["tampered_signature_payload_rejected"])
        self.assertTrue(output["valid_signature_verified"])
        self.assertEqual(output["scope"],"isolated_local_pqc_api_experiment_not_transaction_protocol")

if __name__=="__main__":unittest.main()
