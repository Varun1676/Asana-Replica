from fastapi import APIRouter, Request
from typing import List, Optional, Dict, Any
from app.models.schemas import *

router = APIRouter(tags=['Attachments'])


@router.get("/attachments/{attachment_gid}", response_model=dict | None, summary="Get an attachment")
async def getattachment(request: Request):
    # Implementation pending
    return {}


@router.delete("/attachments/{attachment_gid}", response_model=dict | None, summary="Delete an attachment")
async def deleteattachment(request: Request):
    # Implementation pending
    return {}


@router.get("/attachments", response_model=dict | None, summary="Get attachments from an object")
async def getattachmentsforobject(request: Request):
    # Implementation pending
    return {}


@router.post("/attachments", response_model=dict | None, summary="Upload an attachment")
async def createattachmentforobject(request: Request):
    # Implementation pending
    return {}

