"""Run the illustrative QRCN attack and recovery suite locally."""
from __future__ import annotations
import json
from qrcn import ClearingNetwork, Transaction


def main():
    results = {}
    scenarios = ("normal", "tamper", "stale_tag", "primary_outage",
                 "all_outage", "lost_ack")
    for i, mode in enumerate(scenarios):
        network = ClearingNetwork(key=b"demonstration-only-not-for-production")
        if mode == "primary_outage":
            network.outage.add("alpha")
        if mode == "all_outage":
            network.outage.update(network.nodes)
        if mode == "stale_tag":
            network.rotate_keys()
        fault = {"normal": "none", "primary_outage": "none",
                 "all_outage": "none", "lost_ack": "drop_after_commit"}.get(mode, mode)
        message = Transaction("tx-" + str(i), "payer", "recipient", 10500)
        result = network.clear(message, attack=fault)
        if mode == "lost_ack":
            retry = network.clear(message)
            events = list(result.events) + ["retry:" + retry.status]
        else:
            events = list(result.events)
        results[mode] = {"status": result.status, "route": result.route,
                         "events": events, "ledger": network.snapshot()}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
