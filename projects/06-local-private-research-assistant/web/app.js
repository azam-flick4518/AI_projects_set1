const askButton = document.querySelector("#askButton");
const question = document.querySelector("#question");
const remember = document.querySelector("#remember");
const statusNode = document.querySelector("#status");
const answerNode = document.querySelector("#answer");
const citationsNode = document.querySelector("#citations");
const memoriesNode = document.querySelector("#memories");
const assumptionsNode = document.querySelector("#assumptions");

function setStatus(value) {
  statusNode.textContent = value;
}

function renderList(node, values) {
  node.replaceChildren();
  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = "None";
    node.appendChild(li);
    return;
  }
  for (const value of values) {
    const li = document.createElement("li");
    li.textContent = value;
    node.appendChild(li);
  }
}

async function ask() {
  const payload = {
    question: question.value.trim(),
    remember: remember.value.trim(),
  };
  if (!payload.question) {
    setStatus("Question needed");
    return;
  }

  askButton.disabled = true;
  setStatus("Thinking");
  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }
    answerNode.textContent = data.answer;
    renderList(citationsNode, data.citations || []);
    renderList(memoriesNode, data.memories_used || []);
    renderList(assumptionsNode, data.assumptions || []);
    remember.value = "";
    setStatus("Answered");
  } catch (error) {
    answerNode.textContent = error.message;
    renderList(citationsNode, []);
    renderList(memoriesNode, []);
    renderList(assumptionsNode, []);
    setStatus("Error");
  } finally {
    askButton.disabled = false;
  }
}

askButton.addEventListener("click", ask);
ask();
