# Dockerized Streamlit App

## Dataset Source: 
- https://www.kaggle.com/datasets/smayanj/netflix-users-database
  
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
Dockerfile: Docker configuration for the Python app.
docker-compose.yml: Docker Compose configuration for the services.
requirements.txt: List of Python dependencies.
start.sh: Shell script to run the data ingestion and Streamlit app.
data/: Directory containing the data files (netflix_users.csv).
app.py: Program containing the Streamlit app.

