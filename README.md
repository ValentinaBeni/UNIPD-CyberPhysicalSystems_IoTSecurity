# Cyber-Physical Systems and IoT Security

This repository contains two Python projects developed for the **Cyber-Physical Systems and IoT Security** course at the University of Padua (academic year 2025/2026).

The projects reproduce and analyze two security mechanisms discussed in the scientific literature: mutual authentication for IoT devices using secure vaults, and a denial-of-service attack that exploits CAN bus error handling.

## Repository structure

```text
.
├── Authentication of IoT Device and IoT Server Using Secure Vaults/
│   ├── Report/
│   ├── .env.example
│   ├── DeviceECC.py
│   ├── DeviceVault.py
│   ├── Server.py
│   ├── Vault.py
│   ├── run_ECC.py
│   ├── run_secure_vault.py
│   └── requirements.txt
├── Error Handling of In-vehicle Networks Makes Them Vulnerables/
│   ├── Report/
│   ├── Bus.py
│   ├── Message.py
│   ├── Node.py
│   ├── main.py
│   ├── utils.py
│   └── requirements.txt
└── README.md
```


## Projects

### 1. Authentication of IoT Devices and Servers Using Secure Vaults

This project implements a mutual-authentication protocol in which an IoT device and a server share a collection of cryptographic keys called a **secure vault**. A different subset of keys is combined for each challenge-response exchange, and the vault is updated after every successful session.

The implementation also includes an ECDSA-based authentication mechanism, making it possible to compare the execution time of the secure-vault approach with a conventional public-key solution.

#### Main features

- Multi-step mutual authentication between an IoT device and a server
- Shared-key derivation through XOR operations on selected vault entries
- AES-based encryption of challenge responses
- HMAC-based vault synchronization after successful authentication
- ECDSA authentication using the NIST P-256 curve
- Measurement of encryption, decryption, signing, verification, and vault-update times

#### Project files

| File | Description |
| --- | --- |
| `Vault.py` | Creates, combines, and updates the keys stored in the secure vault |
| `Server.py` | Handles device registration, challenges, verification, and vault synchronization |
| `DeviceVault.py` | Models a device using secure-vault authentication |
| `DeviceECC.py` | Models a device using ECDSA authentication |
| `run_secure_vault.py` | Runs and benchmarks the secure-vault protocol |
| `run_ECC.py` | Runs and benchmarks the ECDSA protocol |

#### Run the project

The original paper implemented the mechanism with an Arduino device, in this project it will
be recreated with a local Python code.
In order to execute the code it's recomended to create a virtual environment and installing the
libraries listed in the file 'requirements.txt', following the commands:

    python -m venv my_venv
    .\my_venv\Scripts\activate
    pip install -r requirements.txt

#### Environment configuration

Before running `run_secure_vault.py`, create a `.env` file inside the project directory. You can
copy the provided example file:

    Copy-Item .env.example .env

The file contains the following configuration:

```dotenv
NUMBER_OF_KEYS=20
KEY_SIZE=16
CHALLENGE_1_LENGTH=4
CHALLENGE_2_LENGTH=3
NUMBER_OF_RUNS=10
```

| Variable | Description |
| --- | --- |
| `NUMBER_OF_KEYS` | Number of cryptographic keys stored in the secure vault |
| `KEY_SIZE` | Size of each key and generated nonce, in bytes |
| `CHALLENGE_1_LENGTH` | Number of vault keys selected for the server challenge |
| `CHALLENGE_2_LENGTH` | Number of vault keys selected for the device challenge |
| `NUMBER_OF_RUNS` | Number of authentication attempts used to calculate the average execution times |

The current implementation expects `KEY_SIZE=16` and `CHALLENGE_2_LENGTH=3`. Both challenge
lengths must not exceed `NUMBER_OF_KEYS`.

Once installed the dependencies, it's sufficient to execute the two main scripts to run the
simulation and then compare the results.

    py run_ECC.py
    py run_secure_vault.py

---

### 2. Error Handling in In-Vehicle Networks and the Bus-Off Attack

This project simulates a **bus-off attack** against a Controller Area Network (CAN). The attack exploits CAN error-handling rules to increase the Transmit Error Counter (TEC) of a legitimate Electronic Control Unit (ECU) until the victim enters the *Bus-Off* state and is disconnected from the network.

Two concurrent ECU nodes transmit messages with the same identifier but different payloads. Once the victim becomes *Error Passive*, the adversarial node manipulates its behavior so that the victim's TEC continues to rise while the attacker's counter decreases.

#### Main features

- Concurrent CAN bus simulation with synchronized message handling
- Concurrent legitimate and adversarial ECU nodes
- CAN error states: *Error Active*, *Error Passive*, and *Bus-Off*
- Message-conflict detection and retransmission modeling
- TEC evolution tracking and visualization
- Reproduction of the attack dynamics described in the reference paper

#### Project files

| File | Description |
| --- | --- |
| `Bus.py` | Models the shared CAN bus and its connected ECUs |
| `Node.py` | Implements ECU behavior, error states, retransmissions, and TEC updates |
| `Message.py` | Represents the messages transmitted by the ECUs |
| `utils.py` | Generates the TEC evolution chart |
| `main.py` | Configures and starts the victim and adversarial nodes |

#### Run the project

While the original paper implemented the attack using real hardware components, this project
reproduces it in a simulated environment using Python, modeling two ECUs and a CAN bus
before executing the attack.

In order to execute the code, it is recommended to create a virtual environment and install the
libraries listed in the file requirements.txt, following the commands:

    python -m venv my_venv
    .\my_venv\Scripts\activate
    pip install -r requirements.txt

Once the dependencies are installed, it is sufficient to execute the main.py script to run the
simulation and analyze the results.

    py main.py
