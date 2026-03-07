from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Metis Report Engine", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test endpoint (before router to avoid conflicts)
@app.get("/test", response_class=PlainTextResponse)
def test():
    """Simple text test endpoint."""
    return "Metis Report Engine is running!"

# Main landing page
@app.get("/", response_class=HTMLResponse)
def root():
    """Landing page with links to API and documentation."""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metis Report Engine</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { color: #4C3D75; }
        .status { 
            padding: 10px 20px; 
            border-radius: 5px; 
            background: #d4edda; 
            color: #155724; 
            display: inline-block; 
        }
        .links { margin: 20px 0; }
        .links a { 
            display: block; 
            padding: 10px; 
            margin: 5px 0; 
            background: #4C3D75; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
        }
        .links a:hover { background: #3a2d5a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Metis Report Engine</h1>
        <div class="status">Server Running</div>
        <p>Version: 0.1.0</p>
        
        <h2>Quick Links</h2>
        <div class="links">
            <a href="/docs">API Documentation (Swagger UI)</a>
            <a href="/redoc">API Documentation (ReDoc)</a>
            <a href="/health">Health Check</a>
        </div>
        
        <h2>API Endpoints</h2>
        <ul>
            <li>POST /compile-dsl - Compile DSL to JSON</li>
            <li>POST /render-html - Render report to HTML</li>
            <li>POST /render-pdf - Render report to PDF</li>
            <li>POST /export-report - Export to various formats</li>
            <li>POST /validate-dsl - Validate DSL syntax</li>
        </ul>
    </div>
</body>
</html>"""

# Include API routes
app.include_router(router)