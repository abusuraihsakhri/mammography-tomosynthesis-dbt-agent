import {evaluateDemo, validatePayload} from "./logic.mjs";

const el = (id) => document.getElementById(id);
let lastResult = null;
let evaluationCount = 0;
let totalAlerts = 0;

el("auditForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const submit = el("submit");
  const feedback = el("feedback");
  const useBackend = el("useBackend").checked;
  feedback.textContent = "";
  const payload = {
    task_id: el("task_id").value.trim(),
    target_identifier: el("target_identifier").value.trim(),
    primary_metric: el("primary_metric").valueAsNumber,
    secondary_metric: el("secondary_metric").valueAsNumber,
    status_descriptor: el("status_descriptor").value.trim(),
    is_critical_flag: el("is_critical_flag").checked
  };
  try {
    validatePayload(payload);
    submit.disabled = true;
    el("modeLabel").textContent = useBackend
      ? "FastAPI evaluation: data sent to the same-origin server."
      : "Browser evaluation: no network request, server-side audit, or signature.";
    let result;
    if (useBackend) {
      const response = await fetch("./api/audit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        throw new Error("Server error (" + response.status + "). Check that the Python API is running and the input is valid.");
      }
      result = await response.json();
    } else {
      result = evaluateDemo(payload);
    }
    lastResult = result;
    evaluationCount += 1;
    totalAlerts += result.total_alerts || 0;
    el("taskCount").textContent = String(evaluationCount);
    el("alertCount").textContent = String(totalAlerts);
    el("lastStatus").textContent = String(result.overall_urgency || "—");
    el("output").textContent = JSON.stringify(result, null, 2);
    el("download").disabled = false;
  } catch (error) {
    feedback.textContent = error instanceof Error ? error.message : "Evaluation failed.";
    el("output").textContent = "Evaluation failed. No substitute or fabricated result was generated.";
  } finally {
    submit.disabled = false;
  }
});

el("download").addEventListener("click", () => {
  if (!lastResult) return;
  const objectUrl = URL.createObjectURL(new Blob([JSON.stringify(lastResult, null, 2) + "\n"], {type: "application/json"}));
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = "dbt-demo-result.json";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
});
