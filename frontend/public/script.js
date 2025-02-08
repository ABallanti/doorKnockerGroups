document.addEventListener('DOMContentLoaded', function() {
    // Disable download button initially
    const downloadButton = document.getElementById("download-clustered-csv");
    downloadButton.disabled = true;
});

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("file");
    const numGroupsInput = document.getElementById("num_groups");
    const mapIframe = document.getElementById("map-display");
    const spinnerOverlay = document.getElementById("spinner-overlay");
    const downloadButton = document.getElementById("download-clustered-csv");

    if (!fileInput.files.length) {
        alert("Please upload a CSV file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("num_groups", numGroupsInput.value);

    // Show the spinner overlay and disable download button
    spinnerOverlay.style.display = "flex";
    downloadButton.disabled = true;

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
        } else {
            // Update iframe source with the generated map through Node.js proxy
            mapIframe.src = `/map/grouped_postcodes_map.html`;
            // Enable download button only after successful processing
            downloadButton.disabled = false;
        }
    } catch (err) {
        console.error(err);
        alert("Failed to process file.");
    } finally {
        // Hide the spinner overlay
        spinnerOverlay.style.display = "none";
    }
});

// Add event listener for the download button
document.getElementById("download-clustered-csv").addEventListener("click", async (event) => {
    // Prevent any default behavior and event bubbling
    event.preventDefault();
    event.stopPropagation();
    
    try {
        // Update to use the Node.js server endpoint instead of direct Python backend
        const response = await fetch('/download-csv');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "grouped_postcodes.csv";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (err) {
        console.error(err);
        alert("Failed to download the clustered data. Make sure you've generated the map first.");
    }
});

// Add event listener for page refresh
window.addEventListener('beforeunload', function() {
    // Disable download button when page is refreshed
    const downloadButton = document.getElementById("download-clustered-csv");
    downloadButton.disabled = true;
});
