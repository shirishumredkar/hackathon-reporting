# Step 1: Use an official lightweight Python runtime environment
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy dependency requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the application code into the container
COPY . .

# Step 5: Inform Docker that the container listens on port 8080
EXPOSE 8080

# Step 6: Run the application using the python runtime engine
# CMD ["python", "app.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2","--timeout", "360", "myproject.wsgi:application"]
