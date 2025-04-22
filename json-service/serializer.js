const axios = require("axios");

const GROQ = process.env.GROQ;

function extractJson(text) {
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("No valid JSON object found in Groq response.");
  }
  return JSON.parse(jsonMatch[0]);
}

async function serializer(ocrText) {
  const prompt = `
You are an AI assistant helping extract structured data from OCR text.

Input documents can be:
- Resume: show raw text (JSON only)
- Invoice: display as a bar graph with item names and prices
- Profit and Loss (P&L): display a bar graph showing revenues and expenses
- Balance Sheet: display a pie chart of asset categories

You must return a strict, valid JSON object in this format:
{
  "type": "<document-type>",
  "displayMode": "json" | "graph",
  "graphType": "bar" | "pie" | "line" | null,
  "graphData": {
    "labels": [string],
    "values": [number]
  } | null
}

IMPORTANT:
- Do not wrap JSON in markdown or code blocks.
- Do not add any explanation before or after the JSON.

Here is the document text:
"""${ocrText}"""
`.trim();

  try {
    const response = await axios.post(
      "https://api.groq.com/openai/v1/chat/completions",
      {
        model: "llama3-8b-8192",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.2,
      },
      {
        headers: {
          Authorization: `Bearer ${GROQ}`,
          "Content-Type": "application/json",
        },
      }
    );

    const content = response.data.choices[0].message.content;

    let parsed;
    try {
      parsed = extractJson(content);
      if (parsed.rawText) {
        parsed.rawText = Buffer.from(parsed.rawText, "base64").toString(
          "utf-8"
        );
      } else {
        parsed.rawText = ocrText;
      }

      if (
        parsed.graphData &&
        Array.isArray(parsed.graphData.labels) &&
        Array.isArray(parsed.graphData.values)
      ) {
        return parsed;
      }

      return {
        type: "unknown",
        displayMode: "json",
        graphType: null,
        graphData: null,
        rawText: ocrText,
      };
    } catch (err) {
      console.error("Invalid JSON from Groq:\n", content);
      return {
        type: "unknown",
        displayMode: "json",
        graphType: null,
        graphData: null,
        rawText: ocrText,
      };
    }
  } catch (err) {
    console.error("Error in serializer:", err.message);
    return {
      type: "unknown",
      displayMode: "json",
      graphType: null,
      graphData: null,
      rawText: ocrText,
    };
  }
}

module.exports = { serializer };
