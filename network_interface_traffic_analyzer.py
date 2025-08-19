###########################################################################################################################
# Python Script that help you to determine which network interfaces are with the highest inbound/outbound traffic counter #
# Created 20/08/2025                                                                                                      #
###########################################################################################################################

##################
# Import Section #
##################

import json
import heapq
import yaml
import requests
import threading
import urllib3
import queue
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

###############
# Global Vars #
###############

# File with Network Configuration
network_config_file = "network_config.yaml"

#######################
# Function Definition #
#######################

# New Worker Function for each thread
def worker(netDev, username, password, result_queue):

    # Auxilear var declaration
    pqin, pqout = [], []

    #Feching data from network device
    jsonVarAux = fetchInfoFromNxos(netDev, username, password)

    # If data is received we add it from biggets_interface_traffic_data function
    if jsonVarAux:
        big_int_int_heapq, big_int_out_heape = biggets_interface_traffic_data(jsonVarAux, pqin, pqout)
        result_queue.put((netDev, pqin, pqout, big_int_int_heapq, big_int_out_heape))

    # If no data is received, we add None info.
    else:
        result_queue.put((netDev, None, None, None, None))

# Function to fetch 'show interface' command from a single router
def fetchInfoFromNxos(NetworkDevice, user, passwd):

    # Header definition for NXAPI Restconf Query
    headers = {'content-type': 'application/json'}

    # Url definition for NXAPI Restconf Query
    url = "https://"+NetworkDevice+"/ins"

    # Payload definition for NXAPI Restconf Query
    payload_show = {
            "ins_api": {
                "version": "1.2",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "show interface",
                "output_format": "json"
            }
        }

    # Saving Restconf query respond from Network Device
    response = requests.post(url, data=json.dumps(payload_show), headers=headers, auth=(user, passwd), verify=False)

    # If we don't receive a HTTP Code as 200 we exit the script 
    if response.status_code == 200:
        return response.json()

    else:
        return {}

# Function Definition
def biggets_interface_traffic_data(jsonData, pqin, pqout):

    # Check if the jsonData is empty before proceeding
    if not jsonData:

        # Return empty heapqs or handle the error as needed
        return None, None

    # Priority Queue for biggets interface In Usage
    big_int_in_heapq = heapq

    # Priority Queue for biggets interface Out Usage
    big_int_out_heape = heapq

    # For each interface detected in the jsonData, we inserted in a Priority Queue for sorting based on highest utilization
    for interface in jsonData['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']:

        # getting interface in usage
        in_bytes = interface.get('eth_inbytes', interface.get('eth_l3in_ucastbytes', interface.get('loop_in_bytes', 0)))

        # getting interface outn usage
        out_bytes = interface.get('eth_outbytes', interface.get('eth_l3out_ucastbytes', interface.get('loop_out_bytes', 0)))

        # Adding interfce "in_bytes" as priority and interface['interface'] as name
        big_int_in_heapq.heappush(pqin, (-int(in_bytes), interface['interface']))

        # Adding interfce "out_bytes" as priority and interface['interface'] as name
        big_int_out_heape.heappush(pqout, (-int(out_bytes), interface['interface']))

    return big_int_in_heapq, big_int_out_heape

# Function that will print on console the highest utilization of the interfaces
def printingHighestInterfaceUtilization(netDev, big_int_in_heapq, big_int_out_heape, pqin, pqout):

    # Printing the Header of the interface utilization
    firstLoop = True

    # Printing interface usage
    if big_int_in_heapq:

        #  Printing interface In usage 
        while pqin:

            # Printing header and disabling firstLoop variable
            if firstLoop:
                print("+----------------------------------------------------------------------+")
                print(f"|                       {netDev:<15}                        |")
                print("+----------------------+-----------------------------------------------+")
                print("|    Interface Name    |    Traffic Interface Utilization In (GB)      |")
                print("+----------------------+-----------------------------------------------+")
                firstLoop = False

            # Removing the hights interface usage from the Priority Queue
            int_in_usage_priority, int_in_usage_name = big_int_in_heapq.heappop(pqin)

            # Printing the hights interface usage from network device
            print(f"|    {int_in_usage_name:<18}|    {str(-(int(int_in_usage_priority)/1073741824)):<43}|")

        print("+----------------------+-----------------------------------------------+")

        # Reinizializate first Loop Var
        firstLoop = True

        #  Printing interface Out usage 
        while pqout:

            # Printing header and disabling firstLoop variable
            if firstLoop:
                print("|    Interface Name    |    Traffic Interface Utilization Out (GB)     |")
                print("+----------------------+-----------------------------------------------+")
                firstLoop = False

            # Removing the hights interface usage from the Priority Queue
            int_out_usage_priority, int_out_usage_name = big_int_out_heape.heappop(pqout)

            # Printing the hights interface usage from network device
            print(f"|    {int_out_usage_name:<18}|    {str(-int(int_out_usage_priority/1073741824)):<43}|")

        print("+----------------------+-----------------------------------------------+")

    else:
            print("No interface data found.")

# Main Function
def main():

    # Variable that load the network config from yaml file
    network_config = {}

    # Initialize an empty list to serve as our priority queue
    pqin, pqout = [], []

    # Thread list for multi threading (concurrency)
    threads = []

    # Auxilear var to save the json info
    jsonVarAux = {}

    #
    result_queue = queue.Queue()

    with open(network_config_file, 'r', encoding='utf-8') as network_config:
        network_config = yaml.safe_load(network_config)

    # For each network device, start a new thread
    for netDev in network_config['NetworkDevice']:

        # Create and start a thread for each device
        thread = threading.Thread(target=worker, args=(
            netDev,
            network_config['Credentials']['username'],
            network_config['Credentials']['password'],
            result_queue
        ))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Process results from the queue after all threads have finished
    while not result_queue.empty():

        # Inizializate variables from queue class
        netDev, pqin, pqout, big_int_int_heapq, big_int_out_heape = result_queue.get()

        # If the queue are not empty we save the data collected in the file
        if big_int_int_heapq and big_int_out_heape:

            # Defining filename based on Network Device Name
            filename = netDev + ".txt"

            # Auxilear Booleans for file printing
            inboundBool, outboundBool = True, True

            try:

                # Open the file with writen mode to save the data collected from network devices
                with open(filename, 'w', encoding='utf-8') as file:

                    # Auxilear Index for file order written
                    index = 1

                    # Moving from priority queue for inbound traffic
                    while pqin:

                        # We feching the bigets interface usage
                        int_in_usage_priority, int_in_usage_name = big_int_int_heapq.heappop(pqin)

                        # Printing inbpund traffic tag in the file
                        if inboundBool:
                            file.write("Inbound Traffic Brief:\n")
                            inboundBool = False

                        # Writing in the file 
                        file.write(f"{str(index)}: Interface: {int_in_usage_name} Usage: {str(-int(int_in_usage_priority/1073741824))} GB\n")

                        # Increasing auxilear variable by 1
                        index += 1

                    # We create a separation in the data collected from inbound traffic and outbound traffic
                    file.write("\n")

                    # Logic for writing outbound traffic to file
                    index = 1

                    # Moving from priority queue for outbound traffic
                    while pqout:

                        # We feching the bigets interface usage
                        int_out_usage_priority, int_out_usage_name = big_int_out_heape.heappop(pqout)

                        # Printing inbpund traffic tag in the file
                        if outboundBool:
                            file.write("Outbound Traffic Brief:\n")
                            outboundBool = False

                        # Writing data from priority queue in the file
                        file.write(f"{str(index)}: Interface: {int_out_usage_name} Usage: {str(-int(int_out_usage_priority/1073741824))} GB\n")

                        # Increasing auxilear variable by 1
                        index += 1

            except Exception as e:
                print(e)

            # Print to CLI if enabled
            if network_config['PrintCLI']:
                printingHighestInterfaceUtilization(netDev, big_int_int_heapq, big_int_out_heape, pqin, pqout)

        else:

            # Print that no interface data collected from network device if the PrintCLI boolean is set to True
            if network_config['PrintCLI']:
                print(f"Skipping {netDev} due to an issue retrieving interface data.")

################
# Main Program #
################

if __name__ == '__main__':
    exit(main())
