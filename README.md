# Network Interface Utilization Monitoring

A Python tool designed for network engineers to collect and analyze interface traffic from Cisco NX-OS devices. It leverages multi-threading and a priority queue to efficiently identify and rank the highest-traffic interfaces, delivering quick reports through the command-line interface (CLI) and text files.

## Features

- **Real-time Traffic Monitoring**: Collects interface traffic data from Cisco NX-OS devices.
- **Multi-threading**: Utilizes multi-threading for efficient data collection from multiple interfaces.
- **Priority Queue**: Ranks interfaces based on traffic load for quick identification of high-utilization interfaces.
- **Reporting**: Generates detailed reports via CLI output and saves them as text files for easy reference.
- **Scalable**: Designed to handle large-scale network environments with multiple devices.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `heapq` (For priority Queue)
  - `queue` (For Priority Queue handled information)
  - `yaml` (For reading network_config.yaml file)
  - `requests` (For NXAPI Restconf Calls)
  - `json` (The return of NXAPI Methods are in json ox xml, i choose json)
  - `threading` (For multi threading)
  - `urllib3` (To disable Certificates expiration validation)
- Cisco NX-OS device with SSH access enabled
- Valid credentials for device access

## Installation

1. Clone the repository:
   ```bash
      git clone https://github.com/NetFreak85/Network-Interface-Utilization-Monitoring.git
      cd Network-Interface-Utilization-Monitoring
   ```

2. Install the required Python libraries:
   ```bash
      pip install -r requirements.txt
   ```

3. Ensure your Cisco NX-OS devices are configured for SSH access and you have the necessary credentials.

## Usage

1. Configure your device details (e.g., IP addresses, credentials) in a configuration file or directly in the script (refer to the script's documentation for details).

2. Run the tool:
   ```bash
      network_interface_traffic_analyzer.py
   ```

3. The tool will:
   
   - Connect to the specified **Cisco NX-OS devices**.
   - Collect interface traffic data using **multi-threading**.
   - Rank interfaces by traffic utilization using a **priority queue**.
   - Display results in the CLI and save them to a text file (e.g., `interface_report.txt`).

Example output:
```
   Inbound Traffic Brief:
   1: Interface: Ethernet1/10 Usage: 3091376 GB
   2: Interface: Ethernet2/10 Usage: 109 GB
   3: Interface: Ethernet1/1 Usage: 24 GB
   4: Interface: Ethernet1/6 Usage: 24 GB
   5: Interface: Ethernet1/3 Usage: 2 GB
   6: Interface: Ethernet1/8 Usage: 2 GB
   7: Interface: Ethernet2/1 Usage: 0 GB
   8: Interface: Ethernet2/2 Usage: 0 GB
   9: Interface: Ethernet2/3 Usage: 0 GB

```

## Configuration

- Edit the configuration file (e.g., `network_config.yaml`) to specify the credentials and the device list:
  ```yaml
     Credentials:

        username : ""     # Username for SSH Authentication
        password : ""     # Password for the Username

     NetworkDevice:
        - router.1.fqdn
        - router.2.fqdn
        - 1.2.3.4
        - 4.5.6.7
  ```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -
