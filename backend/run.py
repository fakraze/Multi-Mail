import uvicorn


if __name__ == "__main__":
    # Authorization codes arrive in callback URLs, so disable request access logs.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, access_log=False)
