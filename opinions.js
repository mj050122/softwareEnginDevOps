// opinions.js
document.addEventListener("DOMContentLoaded", function () {
    loadOpinions();
  });
  
  function loadOpinions() {
    chrome.storage.sync.get("opinions", function (data) {
      const opinions = data.opinions || {};
      const tableBody = document.getElementById("opinionsBody");
  
      // Clear existing rows
      tableBody.innerHTML = "";
  
      // Populate the table with opinions
      Object.entries(opinions).forEach(([url, opinion]) => {
        const row = tableBody.insertRow();
        const cellUrl = row.insertCell(0);
        const cellOpinion = row.insertCell(1);
  
        cellUrl.textContent = url;
        cellOpinion.textContent = opinion; // Updated this line to display opinions
      });
    });
  }
  