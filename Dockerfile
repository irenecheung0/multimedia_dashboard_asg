FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Ensure the shell script has the correct permissions
RUN chmod +x /app/start.sh

# Expose the port that Streamlit uses
EXPOSE 8501

# Command to run the shell script
CMD ["sh", "/app/start.sh"]