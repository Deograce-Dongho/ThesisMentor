let currentDocId = null;
let currentFileUrl = null;

const pdfFile = document.getElementById("pdfFile");
const uploadBtn = document.getElementById("uploadBtn");
const pdfFrame = document.getElementById("pdfFrame");
const statusEl = document.getElementById("status");

const queryEl = document.getElementById("query");
const askBtn = document.getElementById("askBtn");
const answerEl = document.getElementById("answer");
const sourcesEl = document.getElementById("sources");

// ---------- Upload ----------
uploadBtn.addEventListener("click", async () => {
  if (!pdfFile.files.length) {
    statusEl.textContent = "Please choose a PDF first.";
    return;
  }

  statusEl.textContent = "Uploading...";
  const formData = new FormData();
  formData.append("file", pdfFile.files[0]);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      statusEl.textContent = data.error || "Upload failed.";
      return;
    }

    currentDocId = data.doc_id;
    currentFileUrl = data.file_url;
    statusEl.textContent = `Ready: ${data.page_count} pages indexed. Ask a question!`;
    pdfFrame.src = currentFileUrl;
    answerEl.textContent = "";
    sourcesEl.replaceChildren();
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Upload error. Check console.";
  }
});

// ---------- Ask ----------
async function ask() {
  if (!currentDocId) {
    answerEl.textContent = "Upload a PDF first.";
    return;
  }
  const query = queryEl.value.trim();
  if (!query) {
    answerEl.textContent = "Type a question first.";
    return;
  }

  answerEl.textContent = "Searching the document...";
  sourcesEl.replaceChildren();

  try {
    // 1. The backend finds the most relevant pages
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doc_id: currentDocId, query }),
    });
    const data = await res.json();
    if (!res.ok) {
      answerEl.textContent = data.detail || "Ask failed.";
      return;
    }

    if (!data.sources.length) {
      answerEl.textContent = "No page of the document matches this question. Try other keywords.";
      return;
    }
    showSources(data.sources);

    // 2. The AI (Puter.js) writes an answer from those pages
    answerEl.textContent = "Thinking...";
    answerEl.textContent = await askAI(query, data.sources);
  } catch (err) {
    console.error(err);
    answerEl.textContent =
      "The AI is not available right now. Here are the most relevant pages of the document:";
  }
}

askBtn.addEventListener("click", ask);
queryEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") ask();
});

// ---------- AI ----------
async function askAI(query, sources) {
  if (typeof puter === "undefined") throw new Error("Puter.js not loaded");

  const context = sources
    .map((s) => `[Page ${s.label}]\n${s.text}`)
    .join("\n\n");

  const prompt =
    "You are ThesisMentor, an academic assistant helping a student understand a document.\n" +
    "Answer the question using ONLY the excerpts below. Cite the pages like (p. 12).\n" +
    "If the excerpts do not contain the answer, say so honestly.\n" +
    "Answer in the same language as the question.\n\n" +
    `Excerpts:\n${context}\n\nQuestion: ${query}`;

  const response = await puter.ai.chat(prompt);
  return extractText(response);
}

function extractText(response) {
  if (typeof response === "string") return response;
  const content = response?.message?.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) return content.map((c) => c.text || "").join("");
  return String(response);
}

// ---------- Sources ----------
function showSources(sources) {
  const title = document.createElement("h4");
  title.textContent = "Sources in the document:";
  sourcesEl.replaceChildren(title);

  for (const s of sources) {
    const card = document.createElement("button");
    card.className = "source-card";
    card.title = "Open this page in the PDF";

    const label = document.createElement("strong");
    label.textContent = `Page ${s.label}`;
    card.append(label, document.createTextNode(s.snippet));

    card.addEventListener("click", () => {
      // The ?p= part forces the viewer to reload, so it jumps even if the PDF is already open
      const page = s.page_index + 1;
      pdfFrame.src = `${currentFileUrl}?p=${page}#page=${page}`;
    });
    sourcesEl.append(card);
  }
}
