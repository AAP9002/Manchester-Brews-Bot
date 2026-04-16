// ============================================================
// Google Apps Script — Coffee Count Logger
// ============================================================
// SETUP:
// 1. Go to https://script.google.com and create a new project
// 2. Paste this entire script into Code.gs
// 3. Click Deploy > New deployment
// 4. Select type: "Web app"
// 5. Set "Execute as": Me
// 6. Set "Who has access": Anyone
// 7. Click Deploy and copy the Web App URL
// 8. Paste the URL into settings.toml as GOOGLE_SHEET_URL
// ============================================================

const SHEET_NAME = "CoffeeLog";

function getOrCreateSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(["timestamp"]);
  }
  return sheet;
}

// GET request — count all rows (minus header), or log a new entry if ?action=log
function doGet(e) {
  const sheet = getOrCreateSheet();
  if (e && e.parameter && e.parameter.action === "log") {
    const now = new Date().toISOString();
    sheet.appendRow([now]);
  }
  const count = Math.max(0, sheet.getLastRow() - 1);
  return ContentService.createTextOutput(
    JSON.stringify({ count: count })
  ).setMimeType(ContentService.MimeType.JSON);
}

// POST request — log a timestamp
function doPost(e) {
  const sheet = getOrCreateSheet();
  const now = new Date().toISOString();
  sheet.appendRow([now]);
  const count = sheet.getLastRow() - 1;
  return ContentService.createTextOutput(
    JSON.stringify({ count: count })
  ).setMimeType(ContentService.MimeType.JSON);
}
