# dictao

## Introduction

Decentralized Intelligent Contact Tracing of Animals and Objects (DICTAO) is a simple idea to track the COVID-19 pandemic infections.

DICTAO uses IoT, AI and Blockchain technologies to tackle the spread of infection by animals and objects.


## Access the entire book

This repository is a tutorial with instructions to build a simple contact tracing application using the DIApp design pattern. The tutorial is part of the Packt book: _"Hands-On Artificial Intelligence for Blockchain: Converging Blockchain and AI to build smart applications for new economies"_.

You can pre-order the book on [Packt website](https://www.packtpub.com/data/hands-on-artificial-intelligence-for-blockchain), [Amazon global website](https://bit.ly/handson-ai-blockchain-amazon-global-github) or [Amazon India website](https://bit.ly/handson-ai-blockchain-amazon-india-github).

## Instructions



### Dependencies

#### Software

Install the following softwares on your system:

| Sl. No. | Dependency                             | Download link                              |
|---------|----------------------------------------|--------------------------------------------|
| 1       | Just   (v0.5.11 and above)             | https://github.com/casey/just#installation |
| 2       | Python   (v 3 .6.9  and above )        | https://www.python.org/downloads/          |
| 3       | Node. js   ( 12 .18.2 LTS  and above ) | https://nodejs.org/en/download/            |
| 4       | Brave browser  (v 1.5.123 and above )  | https://brave.com/download/                |
| 5       | Jupyter  Notebook                      | https://jupyter.org/install                |


#### Services

Apart from the above software, you will also need to signup for the following services:

1. [Google Maps API](https://developers.google.com/maps/premium/apikey/geolocation-apikey)

2. [MóiBit](https://account.moibit.io/#/signup)

3. [Infura](https://infura.io/register)

4. Ethereum wallet with a wallet address and private key

5. Address of the location proof smart contract (You can use `0x79217e504A28ABCd30D2E90E2C99334FA2e9Fb19` on Kovan)

#### Justfile

Once you have the credentials for all the above 5 services, update your local justfile:
```yaml
export GMAPS_API_KEY := "?"
export MOIBIT_API_KEY := "?"
export MOIBIT_API_SECRET := "?"
export WEB3_INFURA_PROJECT_ID := "?"
export PROOF_SMART_CONTRACT_ADDRESS := "?"
export WALLET_PRIVATE_KEY := "?"
export WALLET_ADDRESS := "?"

run-client:
    python iot-client-code/python/main.py

run-web:
    cd frontend-tracking-dashboard && node index.js

run-server:
    python backend-contact-tracing/server.py

install-dependencies:
    pip install --user -r requirements.txt
    cd frontend-tracking-dashboard && npm install
```

#### Installing python and npm libaries

If you have updated your Jusfile successfully, you need to run the following command to automatically install all the python and Javasript dependencies:

```sh
just install-dependencies
```

Make sure that you are running this command in the same directory where justfile exists.

### Running the app

#### Running the IoT sensor client application

```sh
just run-client
```

#### Running the Contact tracing backend API

```sh
just run-server
```

#### Running the Web dashboard server

```sh
just run-web
```

## License

MIT License

Copyright (c) 2020 Ganesh Prasad Kumble and DICTAO authors
