import yaml
import os
import re
from pathlib import Path

def sanitize_tag(tag):
    return re.sub(r'\W+', '_', tag).lower()

def get_response_model(operation):
    # Try to find a success response with a schema
    for code in ['200', '201', '204']:
        if code in operation.get('responses', {}):
            content = operation['responses'][code].get('content', {})
            if 'application/json' in content:
                schema = content['application/json']['schema']
                if '$ref' in schema:
                    return schema['$ref'].split('/')[-1]
    return "dict"

def generate_routers():
    with open('asana_oas.yaml', 'r') as f:
        spec = yaml.safe_load(f)

    routers_dir = Path('app/routers')
    routers_dir.mkdir(parents=True, exist_ok=True)
    (routers_dir / '__init__.py').touch()

    routes_by_tag = {}

    for path, path_item in spec.get('paths', {}).items():
        for method, operation in path_item.items():
            if method not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            tags = operation.get('tags', ['default'])
            tag = tags[0]
            summary = operation.get('summary', 'No summary')
            operation_id = operation.get('operationId', f"{method}_{path.replace('/', '_')}")
            
            # Clean up operation_id to be a valid python function name
            func_name = re.sub(r'\W+', '_', operation_id).lower()
            
            response_model = get_response_model(operation)
            
            # Build route definition
            route_code = f"""
@router.{method}("{path}", response_model={response_model} | None, summary="{summary}")
async def {func_name}(request: Request):
    # Implementation pending
    return {{}}
"""
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(route_code)

    # Write router files
    for tag, routes in routes_by_tag.items():
        tag_slug = sanitize_tag(tag)
        file_path = routers_dir / f"{tag_slug}.py"
        
        with open(file_path, 'w') as f:
            f.write("from fastapi import APIRouter, Request\n")
            f.write("from typing import List, Optional, Dict, Any\n")
            f.write("from app.models.schemas import *\n\n")
            f.write(f"router = APIRouter(tags=['{tag}'])\n\n")
            
            for route in routes:
                f.write(route + "\n")

    print(f"Generated {len(routes_by_tag)} router files.")

if __name__ == "__main__":
    generate_routers()
