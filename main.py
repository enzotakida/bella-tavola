from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Importando as configurações e as rotas
from config import settings
from routers import pratos, pedidos, reservas, predict

app = FastAPI(
    title=settings.app_name, description=settings.description, version=settings.version
)

# Registrando os departamentos (routers) no app principal
app.include_router(pratos.router)
app.include_router(pedidos.router)
app.include_router(reservas.router)
app.include_router(predict.router, prefix="/ml", tags=["ML"])


@app.get("/", tags=["Home"])
async def root():
    return {
        "restaurante": "Bella Tavola",
        "mensagem": "Testando hot reload!!!",
        "chef": settings.chef,
        "cidade": "São Paulo",
        "especialidade": "Massas artesanais",
    }


# Handlers de Exceção Globais
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": [
                {
                    "campo": " -> ".join(str(loc) for loc in e["loc"]),
                    "mensagem": e["msg"],
                }
                for e in exc.errors()
            ],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url),
            "detalhes": [],
        },
    )
