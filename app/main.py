import uvicorn
from fastapi import FastAPI
from app.router import answer, question, survey, user, auth
from .config import settings

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.include_router(answer.router)
app.include_router(question.router)
app.include_router(survey.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    SAMPLE_ENV_VAR = settings.SAMPLE_ENV_VAR
    return {"ENV": SAMPLE_ENV_VAR}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8008, reload=True)
