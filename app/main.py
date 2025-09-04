import os
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .routers import file_routes

from .routers import auth_router
from .dependencies import get_current_user
from .schemas import TokenData
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import status

app = FastAPI()


# Custom OpenAPI configuration
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FileNest API",
        version="1.0.0",
        description="API for FileNest application",
        routes=app.routes,
    )
    
 
    openapi_schema["components"] = {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token without 'Bearer ' prefix"
            }
        }
    }
    
 
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "dependencies" in method and any(
                dep.dependency == get_current_user 
                for dep in method["dependencies"]
            ):
                method["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(file_routes.router, prefix="/file", tags=["File"])
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # <-- important for Angular
)
@app.get("/")
def read_root():
    return {"message": "Welcome to FileNest - Smart File Organizers"}


if not os.path.exists("uploads"):
    os.makedirs("uploads")

 
@app.get("/me")
async def get_current_user_info(
    request: Request,
    user: TokenData = Depends(get_current_user)
):
    # Get the token from the Authorization header
    authorization: str = request.headers.get("Authorization")
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    # Create response with token in header
    content = {
        "user_id": user.user_id,
        "session_id": user.session_id
    }
    
    response = JSONResponse(content=content)
    response.headers["X-Access-Token"] = token
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
        
    )

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"},
       
    )