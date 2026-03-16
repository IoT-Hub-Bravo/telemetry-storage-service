# IoT Hub Telemetry Storage Service

Service for persisting and querying historical telemetry data in time-series storage.

## Purpose

The Telemetry Storage Service owns the canonical historical telemetry store and provides access to persisted telemetry data.

## Responsibilities

- consume validated telemetry
- persist telemetry to time-series storage
- expose historical query capabilities
- provide recent telemetry views
- support retention and storage lifecycle policies

## Owned data

- telemetry records
- time-series tables or hypertables
- telemetry retention metadata
- recent and historical telemetry views

## Integrations

### Inbound
- validated telemetry topic
- internal API consumers querying telemetry

### Outbound
- telemetry read APIs

## Technology

- Python
- FastAPI
- TimescaleDB / MongoDB
- Docker
