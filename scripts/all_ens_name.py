from web3 import Web3
import json

# Connect to an Ethereum node (replace with your own node URL)
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/PROJECT_ID'))

# ENS Registry contract address
ENS_REGISTRY_ADDRESS = '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e'

# ABI for the ENS Registry contract (simplified)
ENS_REGISTRY_ABI = json.loads('[{"name":"NewOwner","type":"event","inputs":[{"type":"bytes32","name":"node","indexed":true},{"type":"bytes32","name":"label","indexed":true},{"type":"address","name":"owner","indexed":false}]}]')

# Create contract instance
ens_registry = w3.eth.contract(address=ENS_REGISTRY_ADDRESS, abi=ENS_REGISTRY_ABI)

# Function to get ENS names and addresses
def get_ens_names_and_addresses(from_block, to_block):
    events = ens_registry.events.NewOwner.get_logs(fromBlock=from_block, toBlock=to_block)
    for event in events:
        node = event['args']['node'].hex()
        label = event['args']['label'].hex()
        owner = event['args']['owner']
        
        # Resolve the name (this is a simplified approach and may not work for all names)
        try:
            name = w3.ens.name(owner)
            if name:
                print(f"ENS Name: {name}, Address: {owner}")
        except Exception as e:
            print(f"Error resolving name for {owner}: {e}")

# Example usage
start_block = 9000000  # Choose an appropriate starting block
end_block = 'latest'
get_ens_names_and_addresses(start_block, end_block)