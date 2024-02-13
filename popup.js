window.addEventListener("DOMContentLoaded", function () {
  document.getElementById("checkOpinion").addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const url = tabs[0].url;
      chrome.runtime.sendMessage({ action: "checkUrl", url: url }, function (response) {
        if (response && response.opinion) {
          alert(`Opinion about this website: ${response.opinion}`);
        } else {
          alert("No opinion found for this website.");
        }
      });
    });
  });

  document.getElementById("addOpinion").addEventListener("click", function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      const url = tabs[0].url;
      chrome.runtime.sendMessage({ action: "addOpinion", url: url, opinion: prompt("Enter your opinion:") }, function (response) {
        if (response && response.success) {
          alert("Opinion added successfully!");
        } else {
          alert("Failed to add opinion.");
        }
      });
    });
  });

  document.getElementById("loginLink").addEventListener("click", function () {
    chrome.tabs.update({ url: chrome.runtime.getURL("login.html") });
  });  
});
