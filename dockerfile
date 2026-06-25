# ── Estágio 1: builder ──────────────────────────────────────────────────────
# Tem tudo que é necessário para INSTALAR as dependências
# O nome 'builder' é uma convenção — pode ser qualquer nome
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Instala em /install — um diretório separado para facilitar a cópia
# --no-cache-dir: não guarda cache do pip
# --prefix=/install: instala os pacotes em /install em vez de /usr/local
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Estágio 2: final ────────────────────────────────────────────────────────
# Imagem limpa — começa do zero sem nenhum resíduo do builder
FROM python:3.11-slim

WORKDIR /app

# Copia APENAS os pacotes instalados do estágio builder
# --from=builder: instrui o Docker a copiar do estágio anterior
COPY --from=builder /install /usr/local

# Copia o código da aplicação
COPY . .

# Usuário não-root
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]