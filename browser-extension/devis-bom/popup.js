const DEFAULT_API_BASE = "http://localhost:8001";

function extractPriceFromPage() {
  const selectors = [
    '[itemprop="price"]',
    'meta[itemprop="price"]',
    'meta[property="product:price:amount"]',
    ".a-price .a-offscreen",
    ".price",
    ".product-price",
  ];
  for (const selector of selectors) {
    const el = document.querySelector(selector);
    if (!el) continue;
    const raw = el.getAttribute("content") || el.textContent || "";
    const match = raw.replace(/\s/g, "").match(/(\d+[.,]\d{1,2})/);
    if (match) return parseFloat(match[1].replace(",", "."));
  }
  const bodyMatch = document.body.innerText.match(/(\d{1,4}[.,]\d{2})\s*€/);
  return bodyMatch ? parseFloat(bodyMatch[1].replace(",", ".")) : null;
}

async function getApiBase() {
  const { apiBase } = await chrome.storage.sync.get("apiBase");
  return apiBase || DEFAULT_API_BASE;
}

function setStatus(message, ok) {
  const el = document.getElementById("status");
  el.textContent = message;
  el.className = ok ? "ok" : "err";
}

async function activeTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function init() {
  const apiBase = await getApiBase();
  const tab = await activeTab();
  document.getElementById("store").value = tab.url ? new URL(tab.url).hostname : "";

  try {
    const response = await fetch(`${apiBase}/api/lines`);
    const lines = await response.json();
    const select = document.getElementById("line");
    select.innerHTML = "";
    for (const entry of lines) {
      const option = document.createElement("option");
      option.value = entry.line.reference;
      option.textContent = `${entry.line.reference} — ${entry.line.designation}`;
      select.appendChild(option);
    }
    if (lines.length === 0) {
      setStatus("Aucune ligne dans le BOM — ajoute-la d'abord sur la page devis-bom.", false);
    }
  } catch (err) {
    setStatus(`Impossible de joindre l'API (${apiBase}) : ${err.message}`, false);
  }

  try {
    const [{ result }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: extractPriceFromPage,
    });
    if (result != null) {
      document.getElementById("price").value = result;
    }
  } catch (err) {
    // Extraction is best-effort; the user can always type the price manually.
  }
}

document.getElementById("capture").addEventListener("click", async () => {
  const apiBase = await getApiBase();
  const reference = document.getElementById("line").value;
  const price = parseFloat(document.getElementById("price").value);
  const store = document.getElementById("store").value.trim();
  if (!reference) return setStatus("Choisis une ligne du BOM.", false);
  if (!price || price <= 0) return setStatus("Prix invalide.", false);
  if (!store) return setStatus("Nom du magasin manquant.", false);

  const tab = await activeTab();
  try {
    const response = await fetch(`${apiBase}/api/prices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reference, store, price, url: tab.url || "" }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    setStatus("Prix capturé.", true);
  } catch (err) {
    setStatus(`Échec : ${err.message}`, false);
  }
});

document.getElementById("open-options").addEventListener("click", (event) => {
  event.preventDefault();
  chrome.runtime.openOptionsPage();
});

init();
