# Use official python docker image
FROM python:3.11-slim

# Create work directory
WORKDIR /app

# Copy the requirements file 
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the code
COPY . .

# run the server  
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]