import { strict as assert } from "node:assert";
import test from "node:test";
import { assertLineage } from "../contracts/market-to-revenue-v01.js";
import { DeterministicMarketManthanFixture, runMTR001 } from "../src/market-to-revenue/mm-mtr-v01.js";

test("MTR-001 completes MM signal to attributable revenue lineage", () => {
  const slice = runMTR001(new DeterministicMarketManthanFixture());
  assertLineage(slice);
  assert.equal(slice.signal.signal_id, "MM-SIG-001");
  assert.equal(slice.attribution.attributed_amount, 10000);
  assert.equal(slice.attribution.attribution_model, "deterministic_origin_100");
  assert.equal(slice.learning.memory_id, "MEM-001");
});

test("MTR-001 preserves the originating MM provider boundary", () => {
  const slice = runMTR001(new DeterministicMarketManthanFixture());
  assert.equal(slice.signal.provider, "MM-PAF-FIXTURE");
  assert.equal(slice.signal.source, "market-manthan-fixture");
});
