let currentThreadId = null;
let latestAnswerMarkdown = "";
let progressTimer = null;

try { currentThreadId = localStorage.getItem("travel_thread_id"); } catch (e) {}

const $ = (id) => document.getElementById(id);

function setPrompt(text) {
    $("userInput").value = text;
    $("userInput").focus();
}

function setLoading(isLoading) {
    $("sendBtn").disabled = isLoading;
    $("btnText").classList.toggle("hidden", isLoading);
    $("btnLoader").classList.toggle("hidden", !isLoading);
    isLoading ? startProgress() : stopProgress();
}

// The steps follow the order of the LangGraph nodes. They are a visual
// estimate of progress, since the API returns once, when the plan is done.
function startProgress() {
    const items = document.querySelectorAll("#steps li");
    let current = 0;
    const paint = () => items.forEach((li, i) => {
        li.classList.toggle("done", i < current);
        li.classList.toggle("active", i === current);
    });
    $("progress").classList.remove("hidden");
    paint();
    progressTimer = setInterval(() => {
        if (current < items.length - 1) { current++; paint(); }
    }, 6000);
}

function stopProgress() {
    clearInterval(progressTimer);
    $("progress").classList.add("hidden");
}

function showError(message) {
    $("errorBox").textContent = message;
    $("errorBox").classList.remove("hidden");
}

function hideError() {
    $("errorBox").classList.add("hidden");
    $("errorBox").textContent = "";
}

function renderMarkdown(md) {
    if (typeof marked === "undefined") return null;
    const html = marked.parse(md);
    return typeof DOMPurify !== "undefined" ? DOMPurify.sanitize(html) : null;
}

function showResult(answer) {
    latestAnswerMarkdown = answer;
    const html = renderMarkdown(answer);
    if (html) $("resultBox").innerHTML = html;
    else $("resultBox").innerText = answer;
    $("resultSection").classList.remove("hidden");
    $("resultSection").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function sendMessage() {
    hideError();
    const message = $("userInput").value.trim();
    if (!message) {
        showError("Describe your trip first: where you're going, for how long and your budget.");
        return;
    }
    setLoading(true);
    try {
        const response = await fetch("/api/travel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, thread_id: currentThreadId }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || "Something went wrong. Please try again.");
        }
        currentThreadId = data.thread_id;
        try { localStorage.setItem("travel_thread_id", currentThreadId); } catch (e) {}
        showResult(data.answer);
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function newTrip() {
    currentThreadId = null;
    latestAnswerMarkdown = "";
    try { localStorage.removeItem("travel_thread_id"); } catch (e) {}
    $("userInput").value = "";
    $("resultBox").innerHTML = "";
    $("resultSection").classList.add("hidden");
    hideError();
    window.scrollTo({ top: 0, behavior: "smooth" });
    $("userInput").focus();
}

function copyResult() {
    const text = $("resultBox").innerText;
    if (!text) return;
    const btn = document.querySelector(".copy-btn");
    const old = btn.textContent;
    navigator.clipboard.writeText(text)
        .then(() => {
            btn.textContent = "Copied";
            setTimeout(() => (btn.textContent = old), 1400);
        })
        .catch(() => showError("Could not copy the plan."));
}

function downloadPDF() {
    const pdfContent = $("pdfContent");
    if (!latestAnswerMarkdown) {
        showError("There is no plan to download yet.");
        return;
    }
    const btn = document.querySelector(".download-btn");
    const old = btn.textContent;
    btn.textContent = "Preparing PDF...";
    btn.disabled = true;
    const restore = () => { btn.textContent = old; btn.disabled = false; };

    html2pdf()
        .set({
            margin: 0.5,
            filename: "tripmate-travel-plan.pdf",
            image: { type: "jpeg", quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, backgroundColor: "#ffffff" },
            jsPDF: { unit: "in", format: "a4", orientation: "portrait" },
            pagebreak: { mode: ["css", "legacy"] },
        })
        .from(pdfContent)
        .save()
        .then(restore)
        .catch(() => { restore(); showError("Could not create the PDF."); });
}

document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "Enter") sendMessage();
});