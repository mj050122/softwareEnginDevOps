// background.js
chrome.runtime.onInstalled.addListener(function () {
  // Initialize storage with an empty opinions object
  chrome.storage.sync.get("opinions", function (data) {
    if (!data.opinions) {
      chrome.storage.sync.set({ opinions: {} });
    }
  });

  // Initialize user data with a sample user (replace this with a more secure authentication mechanism)
  chrome.storage.sync.get("users", function (data) {
    if (!data.users) {
      chrome.storage.sync.set({ users: { "user1": "password123" } });
    }
  });
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  // Check login credentials
  if (request.action === "checkLogin") {
    const { username, password } = request;
    chrome.storage.sync.get("users", function (data) {
      const users = data.users || {};
      const storedPassword = users[username];
      sendResponse({ success: storedPassword === password });
    });
    return true;
  } else if (request.action === "checkUrl") {
    chrome.storage.sync.get("opinions", function (data) {
      const opinions = data.opinions || {};
      const opinion = opinions[request.url];
      sendResponse({ opinion });
    });
    return true;
  } else if (request.action === "addOpinion") {
    const { url, opinion } = request;
    chrome.storage.sync.get("opinions", function (data) {
      const opinions = data.opinions || {};
      opinions[url] = opinion;
      chrome.storage.sync.set({ opinions }, function () {
        sendResponse({ success: true });
      });
    });
    return true;
  }
});


  