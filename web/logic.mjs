// Deterministic browser demonstration of the numeric rules in agents/workers.py.
// This module is not mammogram interpretation, DBT reconstruction or a medical device.
export const DEMO_RULES = Object.freeze({ primaryCutoff: 25, secondaryCutoff: 12 });

const patterns = [
  /\bMRN[:#\s-]*\d{4,10}\b/i,
  /\b\d{3}-\d{2}-\d{4}\b/,
  /\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/,
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/,
  /\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/i,
  /\b(?:Patient\s+Name|Patient)[:\s]+[A-Z][a-z]+\s+[A-Z][a-z]+\b/i,
  /\b(?:John\s+Doe|Jane\s+Smith|Alice\s+Johnson)\b/i
];

export function validatePayload(value) {
  if (!value || typeof value !== "object") throw new Error("Enter a task payload.");
  for (const field of ["task_id", "target_identifier", "status_descriptor"]) {
    const v = value[field];
    if (typeof v !== "string" || !v.trim() || v.length > (field === "status_descriptor" ? 256 : 128)) {
      throw new Error(field + " must be a nonempty string within the input length limit.");
    }
    if (patterns.some((re) => re.test(v))) throw new Error("Possible identifying information detected. Use synthetic data only.");
  }
  for (const field of ["primary_metric", "secondary_metric"]) {
    if (typeof value[field] !== "number" || !Number.isFinite(value[field])) {
      throw new Error(field + " must be a finite number.");
    }
  }
  if (typeof value.is_critical_flag !== "boolean") throw new Error("is_critical_flag must be true or false.");
  return value;
}

export function evaluateDemo(payload) {
  const p = validatePayload(payload);
  const alerts = [];
  function add(worker, urgency, summary, technicalDetails, remedy) {
    alerts.push({
      alert_id: "DEMO-" + (alerts.length + 1),
      origin_worker: worker,
      urgency,
      summary,
      technical_details: technicalDetails,
      actionable_remediation: remedy,
      standard_reference: "Unvalidated demonstration rules"
    });
  }
  if (p.primary_metric > DEMO_RULES.primaryCutoff) {
    add("InvariantQCWorker", "ELEVATED_RISK", "Primary Metric Threshold Exceeded",
      "Primary measurement (" + p.primary_metric.toFixed(2) + ") exceeds demo cutoff (25.00).",
      "Review the synthetic input and configured cutoff.");
  }
  if (p.is_critical_flag || p.secondary_metric > DEMO_RULES.secondaryCutoff) {
    add("SafetyEscalationWorker", p.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      "Critical Safety Interlock Triggered",
      "CriticalFlag=" + (p.is_critical_flag ? "True" : "False") + " with secondary index " + p.secondary_metric.toFixed(2) + ".",
      "Review the user-supplied critical flag and secondary score; no clinical alert is issued.");
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"]
    .some((word) => p.status_descriptor.toUpperCase().includes(word))) {
    add("ProtocolConformanceWorker", "ELEVATED_RISK", "Protocol Conformance Discordance Detected",
      "Descriptor '" + p.status_descriptor + "' matches a demonstration anomaly keyword.",
      "Review the demonstration status descriptor.");
  }
  const critical = alerts.filter((a) => a.urgency === "CRITICAL_STAT_PANIC").length;
  const elevated = alerts.filter((a) => a.urgency === "ELEVATED_RISK").length;
  const urgency = critical ? "CRITICAL_STAT_PANIC" : elevated ? "ELEVATED_RISK" : "ROUTINE";
  const integrity = critical ? "RECALIBRATION_REQUIRED" : elevated ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL";
  return {
    mode: "BROWSER_DEMONSTRATION",
    task_id: p.task_id,
    target_identifier: p.target_identifier,
    overall_urgency: urgency,
    integrity_status: integrity,
    total_alerts: alerts.length,
    critical_alerts_count: critical,
    alerts,
    consensus_summary: "Demonstration checks completed with status [" + urgency + "]. Total alerts: " + alerts.length + ".",
    audit_hash: null,
    note: "No backend request, image analysis, clinical validation or cryptographic audit signing occurred."
  };
}
