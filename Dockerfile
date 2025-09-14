# Dockerfile

# Use the official BCC base image, which includes kernel headers and dependencies.
# Choose the tag that matches your target kernel version if possible.
FROM bcc/bcc:latest

# Set the working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the image
COPY ./agent /app/agent
COPY ./bpf /app/bpf
COPY ./config /app/config

# Define the command to run the agent
# The agent needs to run as root to load BPF programs.
CMD [ "python3", "agent/shield_agent.py" ]