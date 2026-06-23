# Makefile for Tecticom project

# Variables
IMAGE_NAME = ghcr.io/ronaldfcito/flask-app:latest
STACK_FILE = stack.yml
VPS_USER = $(shell echo $$VPS_USER)
VPS_HOST = $(shell echo $$VPS_HOST)
VPS_SSH_PORT = $(shell echo $$VPS_SSH_PORT)

# Default target
.PHONY: all
all: help

# Help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build      Build Docker image locally"
	@echo "  push       Push image to GitHub Container Registry"
	@echo "  deploy     Deploy stack to VPS (scp stack.yml and Makefile)"
	@echo "  clean      Remove local Docker images"

# Build Docker image
.PHONY: build
build:
	docker build -t $(IMAGE_NAME) .

# Push image to GHCR (requires GHCR_PAT env var)
.PHONY: push
push:
	echo "$(GHCR_PAT)" | docker login ghcr.io -u $(GITHUB_ACTOR) --password-stdin
	docker push $(IMAGE_NAME)

# Deploy to VPS (uses sshpass for password authentication)
.PHONY: deploy
deploy:
	@echo "Copying $(STACK_FILE) and Makefile to VPS..."
	# Using scp-action syntax for consistency with GitHub Actions
	# In local development you can run:
	# scp -P $(VPS_SSH_PORT) $(STACK_FILE) Makefile $(VPS_USER)@$(VPS_HOST):~/despliegue/
	# Then SSH to deploy
	sshpass -p "$(VPS_PASSWORD)" ssh -p $(VPS_SSH_PORT) $(VPS_USER)@$(VPS_HOST) "\
		cd ~/despliegue && \
		docker stack rm tecticom || true && \
		sleep 30 && \
		docker stack deploy -c $(STACK_FILE) --with-registry-auth tecticom\"

# Clean local Docker images
.PHONY: clean
clean:
	docker rmi $(IMAGE_NAME) || true