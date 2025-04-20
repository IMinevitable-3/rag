const express = require("express");
const multer = require("multer");
const path = require("path");
const cors = require("cors");
const { v4: uuidv4 } = require("uuid");
const { extractTextFromImage } = require("./ocrProcessor"); // assumes you have this function

const app = express();
const port = 3000;

app.use(
  cors({
    origin: "http://localhost:4200", // or '*'
    exposedHeaders: ["x-user-token"],
  })
);

app.use(express.json());

// In-memory store for user histories
const userHistory = new Map();

// Middleware: check or issue user token
app.use((req, res, next) => {
  let token = req.header("x-user-token");

  if (!token || typeof token !== "string" || token.trim() === "") {
    token = uuidv4(); // Generate new token
    res.setHeader("x-user-token", token);
  }

  req.userToken = token;

  // Initialize history if not present
  if (!userHistory.has(token)) {
    userHistory.set(token, []);
  }

  next();
});

// Multer config for file uploads
const upload = multer({
  dest: "uploads/",
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.startsWith("image/")) {
      return cb(new Error("Only image files are allowed."));
    }
    cb(null, true);
  },
});

// OCR endpoint
app.post("/api/ocr", upload.single("image"), async (req, res) => {
  try {
    const filePath = path.resolve(req.file.path);
    const text = await extractTextFromImage(filePath);

    const historyItem = {
      filename: req.file.originalname,
      text,
      timestamp: new Date().toISOString(),
    };

    userHistory.get(req.userToken).push(historyItem);

    res.setHeader("x-user-token", req.userToken); // Return token to frontend
    res.json({ text });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to extract text from image." });
  }
});

// History endpoint
app.get("/api/history", (req, res) => {
  try {
    const history = userHistory.get(req.userToken) || [];
    res.setHeader("x-user-token", req.userToken); // make sure it's sent
    res.json({ history }); // MUST be: { history: [...] }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to retrieve history." });
  }
});

// Start server
app.listen(port, () => {
  console.log(`OCR server listening at http://localhost:${port}`);
});
