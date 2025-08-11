# Option 2 note
To run the Strands-enhanced API instead of the default:
- Edit compose/podman-compose.yml and change the traceit-api command to:
  command: ["uvicorn", "api.strands_app:app", "--host", "0.0.0.0", "--port", "8000"]
