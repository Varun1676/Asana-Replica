from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Optional, Dict, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from app.models.schemas import *
import urllib.request
import urllib.error
import urllib.parse
import json

router = APIRouter(tags=['Batch API'])

T = TypeVar("T")
class DataWrapper(BaseModel, Generic[T]):
    data: T

class BatchRequestBody(BaseModel):
    actions: List[BatchRequestAction]

class BatchRequestWrapper(BaseModel):
    data: BatchRequestBody

@router.post("/batch", response_model=DataWrapper[List[BatchResponse]] | None, summary="Submit parallel requests")
async def createbatchrequest(request: Request, body: BatchRequestWrapper):
    actions = body.data.actions
    results = []
    
    # Propagate Authorization header
    auth_header = request.headers.get("Authorization")
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header
        
    # Standard Lib Request to Localhost
    # Assuming port 8000 is reachable via localhost inside container (or 127.0.0.1)
    # The server is listening on 0.0.0.0:8000
    base_url = "http://127.0.0.1:8000" 

    for action in actions:
        method = action.method.value.upper()
        path = action.relative_path
        
        # Prepare URL with Query Params
        query_params = {}
        json_data = None
        
        if method == "GET":
            if action.data:
                query_params.update(action.data)
        else:
            if action.data:
                json_data = {"data": action.data}

        if action.options:
            if action.options.limit is not None:
                query_params["limit"] = action.options.limit
            if action.options.offset is not None:
                query_params["offset"] = action.options.offset
            if action.options.fields is not None:
                query_params["opt_fields"] = ",".join(action.options.fields)
                
        # Encode Query Params
        url = f"{base_url}{path}"
        if query_params:
            url += "?" + urllib.parse.urlencode(query_params)
            
        # Encode Body
        request_body = None
        if json_data:
            request_body = json.dumps(json_data).encode("utf-8")
            
        req = urllib.request.Request(url, data=request_body, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                results.append(BatchResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    body=json.loads(resp_body) if resp_body else {}
                ))
        except urllib.error.HTTPError as e:
             # HTTP Error (4xx, 5xx)
             resp_body = e.read()
             results.append(BatchResponse(
                status_code=e.code,
                headers=dict(e.headers),
                body=json.loads(resp_body) if resp_body else {"detail": str(e)}
             ))
        except Exception as e:
            # Connection error or other
            results.append(BatchResponse(
                status_code=500,
                headers={},
                body={"errors": [{"message": str(e)}]}
            ))
            
    return DataWrapper(data=results)

