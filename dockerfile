# Pick operating system
FROM ubuntu:24.04

# Set non-interactive mode to avoid prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Pick working directory
WORKDIR /root/

# General dependencies and cleanup
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nano git python3.12 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# PAUL dependencies
COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Launch interactive shell by default
CMD ["/bin/bash"]