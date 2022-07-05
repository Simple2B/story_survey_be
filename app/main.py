from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import answer, question, survey, user, auth, stripe, history
from .config import settings

app = FastAPI(
    title=settings.SERVER_NAME,
    docs_url="/backend/docs",
    redoc_url="/backend/redoc",
    openapi_url="/backend/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(answer.router)
app.include_router(question.router)
app.include_router(survey.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(stripe.router)
app.include_router(history.router)


@app.get("/")
def root():
    SAMPLE_ENV_VAR = settings.SAMPLE_ENV_VAR
    return {"ENV": SAMPLE_ENV_VAR}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8009, reload=True)
