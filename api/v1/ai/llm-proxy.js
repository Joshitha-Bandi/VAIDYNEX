export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).send('Method not allowed');

  const { messages, temperature, max_tokens, system_prompt, user_prompt } = req.body;
  
  let finalMessages = messages;
  if (!finalMessages) {
     finalMessages = [
       { role: "system", content: system_prompt || "You are an expert physician clinical scribe." },
       { role: "user", content: user_prompt || "" }
     ];
  }

  const SARVAM_API_KEY = process.env.SARVAM_API_KEY;

  try {
    const response = await fetch("https://api.sarvam.ai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${SARVAM_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "sarvam-105b",
        messages: finalMessages,
        temperature: temperature || 0.2,
        max_tokens: max_tokens || 1000
      })
    });

    const data = await response.json();
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
