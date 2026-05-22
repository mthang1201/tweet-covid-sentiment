import os
import sys
import subprocess
import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Cấu hình CORS để frontend React có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong môi trường dev, cho phép tất cả
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
SRC_DIR = os.path.join(BASE_DIR, 'src')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount thư mục outputs để frontend có thể tải ảnh trực tiếp
app.mount("/static", StaticFiles(directory=OUTPUT_DIR), name="static")

class RunPipelineRequest(BaseModel):
    agg_level: str = "daily"

def run_script(script_name: str, args: list = None):
    script_path = os.path.join(SRC_DIR, script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)

    print(f"\n=== Running {script_name} ===", flush=True)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )

    for line in process.stdout:
        print(line, end="", flush=True)

    process.wait()

    if process.returncode != 0:
        raise Exception(f"Lỗi khi chạy {script_name}")

@app.post("/api/run-pipeline")
def api_run_pipeline(request: RunPipelineRequest):
    agg_level = request.agg_level
    if agg_level not in ["daily", "weekly"]:
        raise HTTPException(status_code=400, detail="Invalid agg_level")
        
    try:
        # Chạy tuần tự các script
        steps = [
            ("01_compute_sentiment.py", []),
            ("02_prepare_cases.py", []),
            ("03_merge_data.py", ["--agg-level", agg_level]),
            ("04_correlation.py", ["--agg-level", agg_level]),
            ("05_plot_temporal.py", ["--agg-level", agg_level]),
            ("06_plot_map.py", ["--agg-level", agg_level]),
        ]

        for i, (script, args) in enumerate(steps, start=1):
            print(f"\n[{i}/{len(steps)}] Starting {script}", flush=True)
            run_script(script, args)
            print(f"[{i}/{len(steps)}] Finished {script}", flush=True)
        
        return {"status": "success", "message": "Pipeline completed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results")
def api_get_results(agg_level: str = "daily"):
    """Trả về kết quả (Global Correlation, tên file ảnh)."""
    global_corr_path = os.path.join(OUTPUT_DIR, f'global_correlation_{agg_level}.txt')
    
    global_corr_text = "N/A"
    if os.path.exists(global_corr_path):
        with open(global_corr_path, 'r') as f:
            global_corr_text = f.read().strip()
            
    # Kiểm tra xem các ảnh đã được tạo chưa
    temporal_img = f"temporal_correlation_{agg_level}.png"
    spatial_img = f"spatial_correlation_map_{agg_level}.png"
    
    return {
        "global_correlation": global_corr_text,
        "temporal_image": f"/static/{temporal_img}" if os.path.exists(os.path.join(OUTPUT_DIR, temporal_img)) else None,
        "spatial_image": f"/static/{spatial_img}" if os.path.exists(os.path.join(OUTPUT_DIR, spatial_img)) else None
    }

if __name__ == "__main__":
    # Use reload_dirs to only watch relevant directories and ignore venv
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["api", "src"],
        reload_excludes=["web/*", "web/node_modules/*", "venv/*", "outputs/*"],
    )
