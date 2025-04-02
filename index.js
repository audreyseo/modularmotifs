'use strict';

const express = require('express');
const path = require('path');
const axios = require("axios");
const fetch = require("node-fetch");
const app = express();

var router = express.Router();

const FLASK_SERVER_URL = "http://127.0.0.1:5000/motif"; // Flask server URL

app.use("/static", express.static(path.join(__dirname, '../react-app/build')));

// app.use((req, res) => {
//     res.status(200).send('Hello, world!');
// });

router.get("/", async (req, res) => {
    try {
        // console.log("req:", req)
        const response = await fetch(FLASK_SERVER_URL)
        // const response = await axios.get(FLASK_SERVER_URL, { responseType: "arraybuffer" });

        // res.setHeader("Content-Type", "image/png");


        console.log(response)
        const data = await response.json()
        console.log(data)
        console.log("Buffer", data)
        res.status(200).send(data)
        // res.send(response.data);
    } catch (error) {
        console.error("Error fetching image:", error.message);
        res.status(500).send("Failed to fetch image from Flask server.");
    }
});

app.use("/fetch-image", router);

// Start the server
const PORT = process.env.PORT || 4000; // 8080;
app.listen(PORT, () => {
    console.log("New app")
    console.log(`App listening on port ${PORT}`);
    console.log('Press Ctrl+C to quit.');
});