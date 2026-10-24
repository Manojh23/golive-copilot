FROM node:24-alpine AS ui
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend ./frontend
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY backend ./backend
COPY data/reference_sources.json data/hospital_benchmark.json data/evaluation_cases.json ./data/
COPY --from=ui /app/dist ./dist
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
