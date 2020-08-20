import yaml
import socket

def activeInventory(boltdir):
    # Read the built inventory file
    with open("{}/inventory.yaml".format(boltdir)) as file:
        loadInventory = yaml.load(file, Loader=yaml.FullLoader)

    # Parse the inventory as JSON
    listOfHosts = []
    inventoryDump = loadInventory['groups'][0]['groups']
    for i in inventoryDump:
        for t in i['targets']:
            listOfHosts.append(t)
    
    return listOfHosts


# Evaluate if the remote host responds to SSH
def evalSocketUptime(host):
    # Opens the Socket    
    sockeval = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Specify what to check
    location = (host,22)
    # Run the Check
    response = sockeval.connect_ex(location)
    # Close the Socket
    sockeval.close()
    # Evaluate the response code
    if response != 0:
        print("{} - SSH is Unresponsive".format(host))

    

