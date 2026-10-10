export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).send('Method not allowed');

  const { text, language_code } = req.body;
  if (!text) return res.status(400).json({ error: "Text is required" });

  const lang = language_code || "te-IN";
  const speakerMap = {
    "te-IN": "kavitha",
    "ta-IN": "kavitha",
    "kn-IN": "kavitha",
    "ml-IN": "kavitha",
    "hi-IN": "priya",
    "mr-IN": "priya",
    "bn-IN": "priya",
    "gu-IN": "priya",
    "pa-IN": "priya",
    "or-IN": "priya",
    "en-IN": "priya"
  };
  const speaker = req.body.speaker || speakerMap[lang] || (["te-IN", "ta-IN", "kn-IN", "ml-IN"].includes(lang) ? "kavitha" : "priya");
  const SARVAM_API_KEY = process.env.SARVAM_API_KEY || "sk_6cogtu4i_AUqyZ8eTmEBU4YvKyO6gYtCi";

  try {
    const response = await fetch("https://api.sarvam.ai/text-to-speech", {
      method: "POST",
      headers: {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        inputs: [text],
        target_language_code: lang,
        speaker: speaker,
        model: "bulbul:v3"
      })
    });

    const data = await response.json();
    if (data.audios && data.audios.length > 0) {
      res.setHeader('Access-Control-Allow-Origin', '*');
      return res.status(200).json({
        audio_base64: data.audios[0],
        language_code: lang,
        engine: "Sarvam Bulbul v3"
      });
    }
    return res.status(500).json({ error: "Failed to generate TTS", details: data });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
