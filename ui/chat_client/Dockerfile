FROM python:3.11-slim

WORKDIR /app

# Copy the chat client code and dependencies
COPY ui/chat_client/chainlit_app.py ./chainlit_app.py
COPY ui/chat_client/auth_app.py ./auth_app.py
COPY ui/chat_client/templates/ ./templates/
COPY ui/chat_client/static/ ./static/
COPY ui/chat_client/start.sh ./start.sh
COPY ui/chat_client/gateway_app.py ./gateway_app.py
COPY events/ ./events/
COPY ui/dashboard/ ./dashboard/
COPY common/ ./common/
COPY .chainlit/ ./.chainlit/

# Copy Python dependencies
COPY ui/chat_client/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make startup script executable
RUN chmod +x ./start.sh

# Expose HTTP port for the gateway
EXPOSE 80

# Run the multi-service startup script
CMD ["./start.sh"]
