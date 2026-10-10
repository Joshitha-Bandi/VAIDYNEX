export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).send('Method not allowed');

  const { text, source_language, target_language } = req.body;
  if (!text) return res.status(400).json({ error: "Text is required" });

  const SARVAM_API_KEY = process.env.SARVAM_API_KEY;

  try {
    const response = await fetch("https://api.sarvam.ai/translate", {
      method: "POST",
      headers: {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        input: text,
        source_language_code: source_language || "hi-IN",
        target_language_code: target_language || "en-IN",
        speaker_gender: "Male",
        mode: "formal",
        model: "mayura:v1"
      })
    });

        const data = await response.json();
    if (data && data.translated_text && data.translated_text.trim().length > 0) {
      res.setHeader('Access-Control-Allow-Origin', '*');
      return res.status(200).json(data);
    }
    throw new Error("Empty translation from Sarvam");
  } catch (error) {
    // Clinical Fallback Translation
    const raw = (text || "").toLowerCase();
    let parts = [];
    if (raw.includes("ఛాతీ") || raw.includes("గుండె") || raw.includes("सीने") || raw.includes("chest") || raw.includes("heart")) parts.push("Chest pain / cardiac distress (EMERGENCY STAT)");
    if (raw.includes("కడుపు") || raw.includes("ఉదరం") || raw.includes("పేట్") || raw.includes("पेट") || raw.includes("stomach") || raw.includes("belly")) parts.push("Stomach / abdominal pain");
    if (raw.includes("మంట") || raw.includes("అజీర్ణం") || raw.includes("గ్యాస్") || raw.includes("जलन") || raw.includes("गैस") || raw.includes("acidity")) parts.push("Acid reflux & epigastric burning");
    if (raw.includes("మోకాలు") || raw.includes("మోకాళ్ళ") || raw.includes("కీళ్ళు") || raw.includes("కీళ్ల") || raw.includes("घुटने") || raw.includes("जोड़ों") || raw.includes("knee") || raw.includes("joint")) parts.push("Knee / joint pain and stiffness");
    if (raw.includes("జ్వరం") || raw.includes("బుఖార్") || raw.includes("बुखार") || raw.includes("fever")) parts.push("Fever and elevated temperature");
    if (raw.includes("చలి") || raw.includes("ఠండ్") || raw.includes("ठंड") || raw.includes("chills")) parts.push("Chills & rigors");
    if (raw.includes("తల") || raw.includes("తలపోటు") || raw.includes("సిర్") || raw.includes("सिर") || raw.includes("headache")) parts.push("Severe headache");
    if (raw.includes("దగ్గు") || raw.includes("ఖాసీ") || raw.includes("खांसी") || raw.includes("cough")) parts.push("Cough / throat irritation");
    if (raw.includes("కన్ను") || raw.includes("కళ్ళు") || raw.includes("ఆంఖ్") || raw.includes("आंख") || raw.includes("eye")) parts.push("Eye pain / irritation");
    if (raw.includes("నడుము") || raw.includes("కమర్") || raw.includes("कमर") || raw.includes("back")) parts.push("Back pain / lumbar stiffness");
    if (raw.includes("నొప్పి") || raw.includes("దర్ద్") || raw.includes("दर्द") || raw.includes("pain")) {
      if (parts.length === 0) parts.push("Localized physical pain");
    }

    const eng = parts.length > 0 ? parts.join(" • ") : (text || "Clinical consultation requested");

    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).json({ translated_text: eng, fallback: true });
  }
}
