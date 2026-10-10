export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  
  res.setHeader('Access-Control-Allow-Origin', '*');
  // Simulated ABDM Creation
  return res.status(200).json({
    abha_number: "91-4829-1029-4821",
    abha_address: "newpatient@abdm",
    status: "SUCCESS"
  });
}
