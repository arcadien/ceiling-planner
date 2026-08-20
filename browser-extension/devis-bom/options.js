const DEFAULT_API_BASE = "http://localhost:8001";

async function load() {
  const { apiBase } = await chrome.storage.sync.get("apiBase");
  document.getElementById("apiBase").value = apiBase || DEFAULT_API_BASE;
}

document.getElementById("save").addEventListener("click", async () => {
  const apiBase = document.getElementById("apiBase").value.trim() || DEFAULT_API_BASE;
  await chrome.storage.sync.set({ apiBase });
  const status = document.getElementById("status");
  status.textContent = "Enregistré.";
  setTimeout(() => (status.textContent = ""), 1500);
});

load();
