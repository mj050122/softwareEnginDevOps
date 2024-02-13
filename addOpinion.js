window.addEventListener("DOMContentLoaded", function () {
    document.getElementById("submitOpinion").addEventListener("click", function () {
      const url = document.getElementById("urlInput").value.trim();
      const opinion = document.getElementById("opinionInput").value.trim();
  
      if (url && opinion) {
        chrome.runtime.sendMessage({ action: "addOpinion", url: url, opinion: opinion }, function (response) {
          if (response && response.success) {
            alert("Opinion added successfully!");
          } else {
            alert("Failed to add opinion.");
          }
        });
      } else {
        alert("Please enter both URL and opinion.");
      }
    });
  });
  