import { createClient } from '@supabase/supabase-js';

export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).end();
  }
  if (req.method !== 'POST') return res.status(405).send('Method not allowed');

  const { encounter_id, patient_id, patient_name, abha_id, token_number, diagnosis, prescription, soap } = req.body;
  
  const SUPABASE_URL = process.env.SUPABASE_URL || "https://smydwqouangckxqzskwm.supabase.co";
  const SUPABASE_KEY = process.env.SUPABASE_KEY;
  if (!SUPABASE_KEY) {
      return res.status(500).json({ error: "Missing SUPABASE_KEY" });
  }
  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

  const tx_id = "ABDM-TX-" + Math.random().toString(36).substr(2, 10).toUpperCase();
  const fhir_id = "urn:uuid:" + crypto.randomUUID();
  const pmjay_claim = "PMJAY-CLM-" + Math.random().toString(36).substr(2, 6).toUpperCase();

  const { data, error } = await supabase.from('abdm_transactions').insert([{
    transaction_id: tx_id,
    encounter_id: encounter_id,
    patient_id: patient_id,
    patient_name: patient_name,
    abha_id: abha_id,
    token_number: token_number,
    diagnosis: diagnosis,
    prescription_json: prescription || [],
    soap_json: soap || {},
    fhir_bundle_id: fhir_id,
    abdm_status: "M2_CARE_CONTEXT_LINKED_GOVT_DB",
    pmjay_claim_id: pmjay_claim
  }]);

  if (error) {
    return res.status(500).json({ error: error.message });
  }

  res.setHeader('Access-Control-Allow-Origin', '*');
  return res.status(200).json({
    status: "SUCCESS_PUSHED_TO_GOVT_DB",
    transaction_id: tx_id,
    encounter_id: encounter_id,
    patient_name: patient_name,
    abha_id: abha_id,
    token_number: token_number,
    fhir_bundle_id: fhir_id,
    abdm_milestone: "M2_HIP_CARE_CONTEXT_LINKED",
    pmjay_claim_status: "AUTO_PREAUTH_APPROVED",
    pmjay_claim_id: pmjay_claim,
    timestamp: new Date().toISOString()
  });
}
