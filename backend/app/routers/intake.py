from fastapi import APIRouter
from ..models.schemas import IntakeChatRequest, IntakeChatResponse
from ..services.clinical_engine import clinical_engine

router = APIRouter(prefix="/intake", tags=["Intake"])

@router.post("/chat", response_model=IntakeChatResponse)
async def chat_step(req: IntakeChatRequest):
    red_flag = clinical_engine.evaluate_red_flag(req.current_input)
    step_idx = len(req.messages) // 2
    reply_text, options, completed = clinical_engine.generate_next_prompt(
        req.current_input, step_idx, req.system_type
    )
    
    if red_flag.is_triggered:
        reply_text = "⚠️ EMERGENCY ALERT DETECTED: Acute symptoms identified. Please move to the Priority Triage Desk immediately."
        options = ["Acknowledge & Call Nurse", "Continue Routine Intake"]

    return IntakeChatResponse(
        reply_text=reply_text,
        suggested_options=options,
        step_completed=completed,
        red_flag=red_flag,
        collected_data={"last_response": req.current_input, "step_index": step_idx}
    )
