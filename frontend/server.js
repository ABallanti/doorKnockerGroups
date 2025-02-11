const fs = require("fs");
const FormData = require("form-data");
const express = require("express");
const multer = require("multer");
const axios = require("axios");
const path = require("path");
require('dotenv').config();

const app = express();
const upload = multer({ dest: "uploads/" }); // Temporary upload directory

// Use environment variables instead of hardcoded values
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5000';

// Serve static frontend files
app.use(express.static("public"));

// Handle file uploads and forward them to the Python backend
app.post("/upload", upload.single("file"), async (req, res) => {
  try {
    // Extract file and number of groups
    const filePath = req.file.path;
    const originalName = req.file.originalname;
    const numGroups = req.body.num_groups || 3;

    // Create FormData object
    const formData = new FormData();
    formData.append("file", fs.createReadStream(filePath), originalName); // Use fs to read the file
    formData.append("num_groups", numGroups);

    // Send file and data to Python backend
    const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
      headers: formData.getHeaders(),
    });

    // Respond with backend results
    res.json(response.data);

    // Cleanup: Remove the uploaded file from the Node.js server
    fs.unlinkSync(filePath);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to process file" });
  }
});

// Add new download route
app.get("/download-csv", async (req, res) => {
  try {
    const response = await axios({
      method: 'get',
      url: `${BACKEND_URL}/download/grouped_postcodes.csv`,
      responseType: 'stream'
    });
    
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=grouped_postcodes.csv');
    
    response.data.pipe(res);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to download file" });
  }
});

// Update map route to handle both placeholder and generated maps
app.get("/map/:mapfile?", async (req, res) => {
    try {
        const mapfile = req.params.mapfile || 'placeholder_map.html';
        console.log('Requesting map:', mapfile);  // Debug log
        
        const response = await axios({
            method: 'get',
            url: `${BACKEND_URL}/download/${mapfile}`,
            responseType: 'text'
        });
        
        console.log('Got response from Flask');  // Debug log
        res.setHeader('Content-Type', 'text/html');
        res.send(response.data);
    } catch (error) {
        console.error('Error details:', error.message);  // More detailed error
        res.status(500).send("Failed to load map");
    }
});

// Start the Node.js server
app.listen(PORT, () => {
  console.log(`Frontend running at port ${PORT}`);
});