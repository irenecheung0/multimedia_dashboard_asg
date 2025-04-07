# Dockerized Streamlit App

## Dataset Source: 
- spotify dataset https://www.kaggle.com/datasets/yelexa/spotify200/data 
- Weather dataset: Daily Total Rainfall All Year - King's Park - https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-total-rainfall 
- Daily Mean Hong Kong Heat Index All Year - King's Park - https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-maximum-mean-heat-index 
- Daily Mean Relative Humidity All Year - King's Park - https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-mean-relative-humidity

  
## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd project-root


2. Build the Docker images:
docker-compose build

3. Start the Docker containers:
docker-compose up

4. Access the Streamlit app in your web browser:
http://localhost:8501


### Project Structure
- Dockerfile: Docker configuration for the Python app.
- docker-compose.yml: Docker Compose configuration for the services.
- requirements.txt: List of Python dependencies.
- start.sh: Shell script to run the data ingestion and Streamlit app.
- data/: Directory containing the data files 
- app.py: Program containing the Streamlit app.

