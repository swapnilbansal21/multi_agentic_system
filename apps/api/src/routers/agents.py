from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.supervisor import run_supervisor

router = APIRouter()


class AgentQueryRequest(BaseModel):
    query: str


@router.post("/agent/query")
async def agent_query(request: AgentQueryRequest) -> dict:
    return await run_supervisor(request.query)
