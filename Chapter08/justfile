export GMAPS_API_KEY := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export MOIBIT_API_KEY := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export MOIBIT_API_SECRET := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export WEB3_INFURA_PROJECT_ID := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export PROOF_SMART_CONTRACT_ADDRESS := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export WALLET_PRIVATE_KEY := "<REPLACE_WITH_YOUR_CREDENTIALS>"
export WALLET_ADDRESS := "<REPLACE_WITH_YOUR_CREDENTIALS>"

run-client:
    python iot-client-code/python/main.py

run-web:
    cd frontend-tracking-dashboard && node index.js

run-server:
    python backend-contact-tracing/server.py

install-dependencies:
    pip install --user -r requirements.txt
    cd frontend-tracking-dashboard && npm install
