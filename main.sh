#!/bin/bash

# Change to the root directory
cd /workspace/DATN/backend || exit 1

# Update and install necessary dependencies
export DEBIAN_FRONTEND=noninteractive

sudo apt-get update && sudo apt-get install -y \
    git \
    build-essential \
    make \
    libssl-dev \
    gcc \
    sudo \
    bash \
    software-properties-common

# Add universe repo (for libsndfile1-dev)
sudo add-apt-repository universe
sudo apt-get update
sudo apt-get install -y libsndfile1-dev

# Clean up
sudo rm -rf /var/lib/apt/lists/*

# Remove old TTS if it exists and clone the new one
rm -rf TTS
git clone -b add-vietnamese-xtts https://github.com/thinhlpg/TTS.git

# Move into the cloned repo and install system dependencies
cd TTS || exit 1
make system-deps
make install

# Go back to root dir
cd /workspace/DATN/backend || exit 1

# Install Python dependencies
pip3 install fugashi[unidic-lite] fugashi[unidic]
python3 -m unidic download

# Upgrade pip
pip3 install --upgrade pip

# Install requirements (adjust path if needed)
pip3 install --default-timeout=90000 -r /workspace/DATN/backend/requirements-vi.txt

# Run the service
sh ./script/start_services_vi.sh
