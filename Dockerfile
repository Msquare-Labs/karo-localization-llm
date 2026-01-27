FROM python:3.11-slim

# Install git for PR creation
RUN apt-get update && \
    apt-get install -y git gh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /action

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python scripts
COPY enforce_100%_translation.py .
COPY apply_translations.py .
COPY add_regional_variants.py .
COPY translate_with_llm.py .

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/action/entrypoint.sh"]
