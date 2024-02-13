document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("submitLogin").addEventListener("click", function () {
      const username = document.getElementById("usernameInput").value.trim();
      const password = document.getElementById("passwordInput").value.trim();
  
      if (username && password) {
        chrome.runtime.sendMessage({ action: "checkLogin", username, password }, function (response) {
          if (response && response.success) {
            alert("Login successful!");
            chrome.tabs.create({ url: chrome.runtime.getURL("opinions.html") });
          } else {
            alert("Invalid credentials. Please try again.");
          }
        });
      } else {
        alert("Please enter both username and password.");
      }
    });
  });
  