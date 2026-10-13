import test from "node:test";
import assert from "node:assert/strict";
import {evaluateDemo, validatePayload} from "./logic.mjs";

const make = (overrides = {}) => ({
  task_id: "TEST-01", target_identifier: "SYNTH-01",
  primary_metric: 10, secondary_metric: 2,
  status_descriptor: "NOMINAL", is_critical_flag: false, ...overrides
});

test("routine inputs have no alerts", () => {
  const d = evaluateDemo(make());
  assert.equal(d.overall_urgency, "ROUTINE");
  assert.equal(d.total_alerts, 0);
  assert.equal(d.audit_hash, null);
});

test("threshold boundaries are strictly greater than", () => {
  assert.equal(evaluateDemo(make({primary_metric: 25, secondary_metric: 12})).total_alerts, 0);
  assert.equal(evaluateDemo(make({primary_metric: 25.01})).total_alerts, 1);
  assert.equal(evaluateDemo(make({secondary_metric: 12.01})).total_alerts, 1);
});

test("critical flag overrides other warnings", () => {
  const d = evaluateDemo(make({primary_metric: 30, is_critical_flag: true, status_descriptor: "ANOMALY"}));
  assert.equal(d.total_alerts, 3);
  assert.equal(d.critical_alerts_count, 1);
  assert.equal(d.overall_urgency, "CRITICAL_STAT_PANIC");
});

test("invalid numeric values and identifiers are rejected", () => {
  for (const v of [NaN, Infinity, -Infinity, "30", null]) {
    assert.throws(() => validatePayload(make({primary_metric: v})), /finite number/);
  }
  assert.throws(() => evaluateDemo(make({task_id: "MRN-123456"})), /identifying/);
  assert.throws(() => evaluateDemo(make({target_identifier: "person@example.com"})), /identifying/);
  assert.throws(() => evaluateDemo(make({status_descriptor: ""})), /nonempty/);
});

test("the demo does not pretend to produce a signed audit", () => {
  const d = evaluateDemo(make({primary_metric: 42}));
  assert.equal(d.mode, "BROWSER_DEMONSTRATION");
  assert.equal(d.audit_hash, null);
  assert.match(d.note, /No backend request/);
});
