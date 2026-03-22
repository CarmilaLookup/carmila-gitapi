// api/index.js
// Fonctionne nativement sur Vercel sans aucune config

const https = require("https");

const GITHUB_KEYS_URL = process.env.GITHUB_KEYS_URL || "";

function fetchKeys() {
  return new Promise((resolve) => {
    if (!GITHUB_KEYS_URL) return resolve({});
    https.get(GITHUB_KEYS_URL, { headers: { "Cache-Control": "no-cache" } }, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve({}); }
      });
    }).on("error", () => resolve({}));
  });
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

module.exports = async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Content-Type", "application/json");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST")    return res.status(405).json({ status: "invalid", message: "Method not allowed" });

  const { key = "", hwid = "unknown" } = req.body || {};
  const cleanKey = key.trim();

  const keys = await fetchKeys();

  if (!cleanKey || !(cleanKey in keys)) {
    return res.status(200).json({ status: "invalid", message: "Cle introuvable.", expires: "" });
  }

  const entry   = keys[cleanKey];
  const expires = entry.expires || "9999-12-31";

  if (today() > expires) {
    return res.status(200).json({ status: "expired", message: "Licence expiree.", expires });
  }

  return res.status(200).json({ status: "valid", message: "Licence valide.", expires });
};
