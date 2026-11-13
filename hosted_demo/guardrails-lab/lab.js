"use strict";

const outcomes = {
  "answer": "Answer released",
  "access-denied": "Account access denied",
  "action-denied": "Action denied",
  "action-recorded": "Simulation receipt recorded",
  "screen-blocked": "Legitimate request wrongly blocked",
  "redacted": "Answer released with contact detail masked",
  "review-held": "Draft held for human review",
  "draft-withheld": "Answer withheld by Governed RAG",
};

const stageList = document.querySelector("#stages");
const stageSummary = document.querySelector("#stage-summary");
const metrics = document.querySelector("#metrics");
const picker = document.querySelector("#case-picker");
const caseResult = document.querySelector("#case-result");

function element(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

function definition(label, value) {
  const pair = document.createElement("div");
  pair.append(element("dt", label), element("dd", value));
  return pair;
}

function initialize(report) {
  let active = report.stages[0];
  const buttons = report.stages.map((stage) => {
    const button = element("button", stage.name);
    button.type = "button";
    button.addEventListener("click", () => {
      active = stage;
      render();
    });
    stageList.append(button);
    return button;
  });
  for (const item of report.cases) {
    const option = element("option", item.title);
    option.value = item.id;
    picker.append(option);
  }
  picker.disabled = false;
  picker.addEventListener("change", render);
  render();

  function render() {
    buttons.forEach((button, index) => {
      button.setAttribute("aria-pressed", String(report.stages[index] === active));
    });
    stageSummary.textContent = active.summary;
    metrics.replaceChildren(
      definition("Expected outcomes", `${active.metrics.expected_outcomes}/${report.cases.length}`),
      definition("Legitimate requests blocked", active.metrics.false_blocks),
      definition("Contact details released", active.metrics.contact_releases),
      definition("Unauthorized actions recorded", active.metrics.unauthorized_actions),
    );
    const selected = report.cases.find((item) => item.id === picker.value);
    const result = active.cases.find((item) => item.case === selected.id);
    const trace = document.createElement("dl");
    trace.className = "trace";
    trace.append(
      definition("Draft writer called", result.draft_requested ? "Yes" : "No"),
      definition("Answer released", result.released ? "Yes" : "No"),
      definition("Contact detail released", result.contact_released ? "Yes" : "No"),
      definition("Action recorded", result.action_recorded ? "Yes, simulation only" : "No"),
    );
    caseResult.replaceChildren(
      element("h3", outcomes[result.outcome]),
      element("p", selected.description),
      element("p", result.reason),
      trace,
    );
  }
}

fetch("results.json")
  .then((response) => {
    if (!response.ok) throw new Error("Unable to load the recorded evaluation.");
    return response.json();
  })
  .then(initialize)
  .catch(() => {
    caseResult.replaceChildren(element("p", "The recorded evaluation could not load. Try refreshing the page."));
  });
