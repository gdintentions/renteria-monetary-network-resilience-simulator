"""Optional local post-quantum API experiment, NOT integrated with transaction transport.

Requires pqcrypto==1.0.0. Generates ephemeral keys in memory, demonstrates
ML-KEM-768 shared-secret agreement and ML-DSA-65 transaction signing.
No keys or secrets are emitted to logs. No security certification implied.
"""
from __future__ import annotations
import json
import statistics
import time
from qrcn.core import Transaction


def milliseconds(fn, n=12):
    samples=[]
    for _ in range(n):
        started=time.perf_counter()
        fn()
        samples.append((time.perf_counter()-started)*1000)
    return {"median_ms":round(statistics.median(samples),4),
            "max_ms":round(max(samples),4),
            "iterations":n}


def run():
    from pqcrypto.kem import ml_kem_768
    from pqcrypto.sign import ml_dsa_65

    # Actual FIPS-algorithm implementations come from a third-party package;
    # this is only an API smoke test, not a cryptographic certification.
    kem_public,kem_secret=ml_kem_768.keygen()
    ciphertext, sender_shared=ml_kem_768.encaps(kem_public)
    receiver_shared=ml_kem_768.decaps(kem_secret,ciphertext)
    if sender_shared != receiver_shared:
        raise AssertionError("ML-KEM secret mismatch")
    bad_ciphertext=bytearray(ciphertext)
    bad_ciphertext[0] ^= 1
    # FO-transform-based KEM may yield a different secret rather than an error.
    bad_secret=ml_kem_768.decaps(kem_secret,bytes(bad_ciphertext))
    altered_ciphertext_changes_secret=(bad_secret!=receiver_shared)

    sign_public,sign_secret=ml_dsa_65.keygen()
    message=Transaction("pqc-demo","alice","bob",12500).encode()
    signature=ml_dsa_65.sign(sign_secret,message)
    ml_dsa_65.verify(sign_public,message,signature)
    tampered=message+b"!"
    rejected=False
    try:
        ml_dsa_65.verify(sign_public,tampered,signature)
    except Exception:
        rejected=True
    if not rejected:
        raise AssertionError("ML-DSA accepted altered signed message")

    kem_ms=milliseconds(lambda: ml_kem_768.encaps(kem_public))
    sig_ms=milliseconds(lambda: ml_dsa_65.sign(sign_secret,message))
    verify_ms=milliseconds(lambda: ml_dsa_65.verify(sign_public,message,signature))
    return {
        "scope":"isolated_local_pqc_api_experiment_not_transaction_protocol",
        "library":"pqcrypto", "version":"1.0.0",
        "kem":"ML-KEM-768", "signature":"ML-DSA-65",
        "shared_secret_matches":True,
        "altered_ciphertext_changes_secret":altered_ciphertext_changes_secret,
        "valid_signature_verified":True,
        "tampered_signature_payload_rejected":rejected,
        "key_sizes_bytes":{
            "kem_public":len(kem_public),"kem_secret":len(kem_secret),
            "kem_ciphertext":len(ciphertext),
            "kem_shared_secret":len(sender_shared),
            "dsa_public":len(sign_public),"dsa_secret":len(sign_secret),
            "dsa_signature":len(signature)
        },
        "warm_cpu_api_timings":{
            "kem_encapsulation":kem_ms,"dsa_sign":sig_ms,
            "dsa_verify":verify_ms},
        "limitations":[
            "Not integrated with transport or clearing", "Ephemeral keys only",
            "No identity authentication, KDF, transcript binding, hybrid mode or KEM-based AEAD",
            "No third-party audit or FIPS 140 module validation",
            "No QKD or quantum hardware",
            "Not an end-to-end latency benchmark"
        ]
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
