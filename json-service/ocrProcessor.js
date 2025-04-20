const fs = require("fs");
const path = require("path");
const sharp = require("sharp");
const Tesseract = require("tesseract.js");

/**
 * Preprocess image using Sharp (resize, grayscale, etc.)
 * @param {string} imagePath
 * @returns {Promise<Buffer>}
 */
async function preprocessImage(imagePath) {
  try {
    const processedImageBuffer = await sharp(imagePath)
      .grayscale()
      .normalize()
      .toBuffer();
    return processedImageBuffer;
  } catch (err) {
    throw new Error(`Image preprocessing failed: ${err.message}`);
  }
}

/**
 * Perform OCR on an image file
 * @param {string} imagePath - The path to the image file
 * @returns {Promise<string>} - Extracted text
 */
async function extractTextFromImage(imagePath) {
  try {
    if (!fs.existsSync(imagePath)) {
      throw new Error("Image file does not exist.");
    }

    const buffer = await preprocessImage(imagePath);

    const {
      data: { text },
    } = await Tesseract.recognize(buffer, "eng", {
      logger: (m) =>
        console.log(
          `[Tesseract]: ${m.status} - ${Math.round(m.progress * 100)}%`
        ),
    });

    return text.trim();
  } catch (err) {
    console.error(`[OCR ERROR]: ${err.message}`);
    throw err; // rethrow so it can be handled by the caller
  }
}

/**
 * Example usage
 */
async function runOCR() {
  const imagePath = path.join(__dirname, "sample-image.png"); // replace with your image path

  try {
    const extractedText = await extractTextFromImage(imagePath);
    console.log("\n📝 Extracted Text:\n", extractedText);
  } catch (err) {
    console.error("Failed to extract text from image:", err.message);
  }
}

// Uncomment this line to run the script standalone
// runOCR();

module.exports = {
  extractTextFromImage,
};
