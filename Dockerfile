# Stage 1: Build the React Frontend
FROM node:20 AS frontend-builder

WORKDIR /app/frontend

# Copy frontend config and source
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
# Build Vite project to generate the static files in /app/frontend/dist
RUN npm run build


# Stage 2: Build the Python Backend
FROM python:3.10-slim

# Set environment variables for huggingface and python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # HuggingFace requires applications to run on port 7860
    PORT=7860 

# Create user with UID 1000 to meet HuggingFace Spaces requirements
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory to the user's home
WORKDIR $HOME/app

# Copy the built frontend from Stage 1
COPY --from=frontend-builder --chown=user /app/frontend/dist $HOME/app/frontend/dist

# Install backend dependencies
COPY --chown=user backend/requirements.txt $HOME/app/backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r $HOME/app/backend/requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the rest of the backend files
COPY --chown=user backend/ $HOME/app/backend/

# Expose the HF port
EXPOSE 7860

# Command to run the application (start FastAPI from the backend directory)
WORKDIR $HOME/app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
