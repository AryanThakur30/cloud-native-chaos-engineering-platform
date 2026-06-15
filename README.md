# Cloud-Native Chaos Engineering Platform for Kubernetes

A production-inspired Chaos Engineering platform built using Kubernetes, FastAPI, Prometheus, Grafana, Docker and Minikube.

## Overview

This project enables controlled fault injection experiments in Kubernetes environments to evaluate system resilience and observability.

The platform exposes REST APIs for triggering chaos experiments and monitoring cluster health.

## Features

* Pod Kill Experiment
* CPU Stress Experiment
* Memory Stress Experiment
* Network Chaos Simulation
* Cluster Health Monitoring
* Experiment History Tracking
* Kubernetes API Integration
* Prometheus Monitoring
* Grafana Visualization

## Architecture

User → FastAPI → Kubernetes API → Minikube Cluster

Prometheus → Metrics Collection

Grafana → Visualization Dashboard

## API Endpoints

| Method | Endpoint                   | Description                  |
| ------ | -------------------------- | ---------------------------- |
| GET    | /                          | Health Check                 |
| POST   | /experiments/pod-kill      | Delete a target pod          |
| POST   | /experiments/cpu-stress    | Generate CPU load            |
| POST   | /experiments/memory-stress | Generate Memory load         |
| POST   | /experiments/network-chaos | Simulate network disruption  |
| GET    | /pods                      | List running pods            |
| GET    | /history                   | Experiment execution history |
| GET    | /cluster-health            | Cluster health statistics    |

## Technology Stack

* Python
* FastAPI
* Kubernetes
* Docker
* Minikube
* Prometheus
* Grafana

## Future Enhancements

* Real Network Latency Injection
* Dashboard UI
* Experiment Scheduling
* RBAC Support
* Multi-Cluster Management
* CI/CD Pipeline

## Learning Outcomes

* Kubernetes Administration
* Chaos Engineering Principles
* Cloud Native Architecture
* Observability and Monitoring
* API Development with FastAPI
* Infrastructure Automation

## Author

Aryan Thakur
