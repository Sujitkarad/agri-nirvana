import { sendAgriAIChat } from "../lib/aiChat";

let conversationHistory = [];

const DEFAULT_FOLLOW_UPS = [
  "Explain this in simple language",
  "What information do you need from my field?",
  "What should I check next?"
];

export function clearConversationHistory() {
  conversationHistory = [];
}

export function getConversationHistory() {
  return [...conversationHistory];
}

export async function generateAIChatResponse({
  userPrompt = "",
  attachments = [],
  selectedModel,
  userLang = "en",
  crop = "Unknown",
  diagnosis = null
}) {
  const prompt = String(userPrompt || "").trim();
  if (!prompt && attachments.length === 0) {
    throw new Error("Please enter a question or attach a crop image.");
  }

  const userContent = prompt || "I attached a crop image. Help me understand what I should do next.";
  const attachmentContext = attachments.length
    ? `\nAttached files: ${attachments.map((file) => file.name || "image").join(", ")}. Use the Crop Diagnosis feature for actual image diagnosis.`
    : "";

  const nextHistory = [
    ...conversationHistory,
    { role: "user", content: `${userContent}${attachmentContext}` }
  ].slice(-12);

  const startTime = Date.now();
  const response = await sendAgriAIChat({
    messages: nextHistory,
    crop,
    language: userLang,
    model: selectedModel,
    diagnosis
  });

  if (!response?.success || !response.message) {
    throw new Error("The AI assistant did not return a valid response.");
  }

  const latency = `${Date.now() - startTime}ms`;

  conversationHistory = [
    ...nextHistory,
    { role: "assistant", content: response.message }
  ].slice(-12);

  return {
    text: response.message,
    source: `${response.model || selectedModel || "Gemini 2.5 Flash"} Neural Inference Engine`,
    reasoning: `Agronomic query processed with ${response.provider || "Gemini"} context (${crop}, ${userLang}) in ${latency}.`,
    latency,
    tableData: null,
    suggestedFollowUps: [
      "Calculate fertilizer dosage for my field",
      "Show organic bio-pesticide alternatives",
      "What are today's APMC mandi prices?"
    ]
  };
}
