"""
Main entrypoint to run the Medi-Caps University QA & Conflict Detection server.
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Medi-Caps University Academic Regulations QA Service on http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
