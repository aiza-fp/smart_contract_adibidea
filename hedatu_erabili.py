"""
Python application to deploy and interact with the Formularioak smart contract.
This script connects to Ethereum nodes, deploys the contract, and performs operations.
"""

import json
import os
from web3 import Web3
from eth_account import Account

# Hardcoded list of IP addresses to try connecting to (port 8545)
IP_LIST = [
    "85.190.243.52",
    # Add more IP addresses as needed
]

def connect_to_provider(ip_list):
    """
    Try to connect to a web3 provider from the IP list.
    Returns a Web3 instance if connection is successful.
    """
    for ip in ip_list:
        try:
            provider_url = f"http://{ip}:8545"
            print(f"Attempting to connect to {provider_url}...")
            w3 = Web3(Web3.HTTPProvider(provider_url))
            
            # Test the connection by checking if we can get the latest block
            if w3.is_connected():
                print(f"Successfully connected to {provider_url}")
                return w3
            else:
                print(f"Connection to {provider_url} failed: Not connected")
        except Exception as e:
            print(f"Connection to {provider_url} failed: {str(e)}")
            continue
    
    raise Exception("Failed to connect to any provider in the IP list")

def create_private_key():
    """
    Generate a new Ethereum private key and return the account.
    Returns the account object with address and private key.
    """
    # Create a new account with a random private key
    account = Account.create()
    print(f"\nGenerated new Ethereum account:")
    print(f"  Address: {account.address}")
    print(f"  Private Key: {account.key.hex()}")
    return account

def load_contract_files():
    """
    Load the contract bytecode and ABI from files.
    Returns tuple (bytecode, abi).
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load bytecode
    bytecode_path = os.path.join(script_dir, "Formularioak.bytecode")
    with open(bytecode_path, "r") as f:
        bytecode_raw = f.read().strip()
    
    # Clean and validate bytecode
    # Remove any whitespace and ensure it's valid hex
    bytecode_clean = ''.join(bytecode_raw.split())
    
    # Check if it starts with 0x, if not add it
    if not bytecode_clean.startswith("0x"):
        bytecode_clean = "0x" + bytecode_clean
    
    # Validate that it's all hex characters
    hex_part = bytecode_clean[2:] if bytecode_clean.startswith("0x") else bytecode_clean
    if not all(c in '0123456789abcdefABCDEF' for c in hex_part):
        raise Exception(f"Invalid bytecode: contains non-hexadecimal characters")
    
    # Check if bytecode length is even (each byte is 2 hex chars)
    if len(hex_part) % 2 != 0:
        raise Exception(f"Invalid bytecode: odd number of hex characters")
    
    bytecode = bytecode_clean
    
    # Load ABI
    abi_path = os.path.join(script_dir, "Formularioak.abi")
    with open(abi_path, "r") as f:
        abi = json.load(f)
    
    # Validate bytecode format
    bytecode_bytes = len(hex_part) // 2
    print(f"\nLoaded contract files:")
    print(f"  Bytecode length: {len(hex_part)} hex characters ({bytecode_bytes} bytes)")
    print(f"  Bytecode starts with: {bytecode[:20]}...")
    print(f"  ABI loaded successfully")
    
    # Check if bytecode looks valid (should start with common Solidity patterns)
    if not bytecode.startswith("0x6080"):
        print(f"  Warning: Bytecode doesn't start with expected Solidity pattern (0x6080)")
    
    # Inspect the bytecode for EVM version compatibility issues
    # Check for PUSH0 (0x5f) which requires Shanghai EVM or later
    push0_found = []
    for i in range(min(100, bytecode_bytes)):  # Check first 50 bytes
        byte_val = hex_part[i*2:(i*2)+2].upper()
        if byte_val == '5F':  # PUSH0 opcode
            push0_found.append(f"position {i}")
    
    if push0_found:
        print(f"  WARNING: Bytecode contains PUSH0 (0x5f) opcode at: {', '.join(push0_found[:5])}")
        print(f"  PUSH0 requires Shanghai EVM upgrade (EIP-3855) or later")
        print(f"  If your Besu network uses an older EVM version, this will cause INVALID_OPERATION errors")
        print(f"  Solution: Recompile the contract with an older Solidity version (e.g., 0.8.19) that targets an older EVM")
        print(f"  Or configure Besu to use Shanghai/Cancun EVM version")
    
    # Check for INVALID opcode (0xFE) in the first 50 bytes
    invalid_found = []
    for i in range(min(50, bytecode_bytes)):
        byte_val = hex_part[i*2:(i*2)+2].upper()
        if byte_val == 'FE':
            invalid_found.append(f"0xFE at position {i}")
    
    if invalid_found:
        print(f"  WARNING: Found INVALID opcode (0xFE) at: {', '.join(invalid_found)}")
        print(f"  This suggests the bytecode may be corrupted or contain invalid data")
    
    return bytecode, abi

def deploy_contract(w3, account, bytecode, abi):
    """
    Deploy the contract to the blockchain.
    Returns the deployed contract instance and contract address.
    """
    # Set the default account for transactions
    w3.eth.default_account = account.address
    
    # Get network information
    try:
        chain_id = w3.eth.chain_id
        print(f"  Network chainId: {chain_id}")
    except Exception as e:
        print(f"  Warning: Could not get chainId from network: {e}")
        chain_id = 1337  # Default for private networks
        print(f"  Using default chainId: {chain_id}")
    
    # Check account balance (informational only - not needed for zero-gas network)
    balance = w3.eth.get_balance(account.address)
    print(f"  Account balance: {balance} wei ({w3.from_wei(balance, 'ether')} ETH)")
    print(f"  Note: Using zero-gas configuration for private Besu network")
    
    # Get the nonce for the account
    nonce = w3.eth.get_transaction_count(account.address)
    print(f"  Account nonce: {nonce}")
    
    # Create the contract deployment transaction
    contract = w3.eth.contract(bytecode=bytecode, abi=abi)
    
    # Calculate minimum intrinsic gas needed based on bytecode size
    # Intrinsic gas = 21000 (base) + 32000 (contract creation) + 200 per bytecode byte
    bytecode_size = len(bytecode) - 2 if bytecode.startswith("0x") else len(bytecode)  # Subtract 2 for "0x" prefix
    bytecode_bytes = bytecode_size // 2  # Each hex char represents 4 bits, so 2 chars = 1 byte
    intrinsic_gas = 21000 + 32000 + (200 * bytecode_bytes)
    print(f"  Bytecode size: {bytecode_bytes} bytes")
    print(f"  Minimum intrinsic gas: {intrinsic_gas}")
    
    # Build the transaction
    # Use network chainId and gasPrice 0 for zero-gas private Besu network
    print(f"\nDeploying contract...")
    transaction = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 0x7FFFFFFF, # Max gas limit for deployment
        "gasPrice": 0,   # Zero gas for private Besu network
        "chainId": chain_id,
    })
    
    # Sign the transaction
    signed_txn = account.sign_transaction(transaction)
    
    # Send the transaction
    print(f"  Transaction hash: {signed_txn.hash.hex()}")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    # Wait for transaction confirmation
    print(f"  Waiting for transaction confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)
    
    # Check if transaction was successful
    if tx_receipt.status != 1:
        # Try to get more information about the failure
        error_msg = f"Contract deployment failed with status: {tx_receipt.status}"
        
        # Check if there's a revert reason in the receipt
        if hasattr(tx_receipt, 'revertReason') and tx_receipt.revertReason:
            error_msg += f"\n  Revert reason: {tx_receipt.revertReason}"
        
        # Check gas used
        if hasattr(tx_receipt, 'gasUsed'):
            error_msg += f"\n  Gas used: {tx_receipt.gasUsed}"
        
        raise Exception(error_msg)
    
    # Get the contract address from the receipt
    contract_address = tx_receipt.contractAddress
    print(f"  Contract deployed at address: {contract_address}")
    print(f"  Block number: {tx_receipt.blockNumber}")
    print(f"  Transaction status: Success")
    
    # Create contract instance
    deployed_contract = w3.eth.contract(address=contract_address, abi=abi)
    
    return deployed_contract, contract_address

def send_transaction(w3, account, contract, function_call, description):
    """
    Generic function to send a transaction to the contract.
    Args:
        w3: Web3 instance
        account: Account object
        contract: Contract instance
        function_call: The contract function call (e.g., contract.functions.createForm(...))
        description: Description of what the transaction does
    Returns:
        Transaction receipt
    """
    print(f"\n{description}...")
    
    # Get the nonce for the account
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Get chainId from network
    try:
        chain_id = w3.eth.chain_id
    except Exception as e:
        print(f"  Warning: Could not get chainId from network: {e}")
        chain_id = 1337  # Default for private networks
    
    # Build the transaction
    transaction = function_call.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 0x7FFFFFFF,  # Max gas limit for function calls
        "gasPrice": 0,      # Zero gas for private Besu network
        "chainId": chain_id,
    })
    
    # Sign the transaction
    signed_txn = account.sign_transaction(transaction)
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"  Transaction hash: {tx_hash.hex()}")
    
    # Wait for transaction confirmation
    print(f"  Waiting for transaction confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)
    print(f"  Transaction confirmed in block: {tx_receipt.blockNumber}")
    
    # Check if transaction was successful
    if tx_receipt.status != 1:
        raise Exception(f"Transaction failed with status: {tx_receipt.status}")
    print(f"  Transaction status: Success")
    
    return tx_receipt

def create_form(w3, account, contract, datu1, datu2):
    """
    Create a new form using the createForm function.
    Returns tuple (transaction_receipt, form_number).
    The form_number is the zenbakia assigned to the newly created form.
    Extracts the form number from the FormCreated event in the transaction receipt.
    """
    function_call = contract.functions.createForm(datu1, datu2)
    receipt = send_transaction(w3, account, contract, function_call, f"Creating form with datu1='{datu1}', datu2='{datu2}'")
    
    # Extract the form number (zenbakia) from the FormCreated event
    # The event is emitted with the formCount as zenbakia
    form_number = None
    for log in receipt['logs']:
        try:
            # Try to decode the log as a FormCreated event
            decoded_event = contract.events.FormCreated().process_log(log)
            form_number = decoded_event['args']['zenbakia']
            print(f"  Form created with zenbakia: {form_number}")
            break
        except:
            # Not a FormCreated event, continue
            continue
    
    if form_number is None:
        raise Exception("Could not extract form number from FormCreated event")
    
    return receipt, form_number

def update_form(w3, account, contract, zenbakia, datu1, datu2):
    """
    Update an existing form using the updateForm function.
    Returns the transaction receipt.
    """
    function_call = contract.functions.updateForm(zenbakia, datu1, datu2)
    return send_transaction(w3, account, contract, function_call, f"Updating form {zenbakia} with datu1='{datu1}', datu2='{datu2}'")

def get_form(contract, zenbakia):
    """
    Retrieve form data using the getForm function (view function, no transaction needed).
    Returns tuple (datu1, datu2).
    """
    print(f"\nRetrieving form data (zenbakia = {zenbakia})...")
    try:
        form_data = contract.functions.getForm(zenbakia).call()
        print(f"  Retrieved form data:")
        print(f"    datu1: {form_data[0]}")
        print(f"    datu2: {form_data[1]}")
        return form_data
    except Exception as e:
        raise Exception(f"Could not retrieve form {zenbakia}: {str(e)}")

def get_events(w3, contract, contract_address, zenbakia, from_block=0):
    """
    Retrieve FormCreated and FormUpdated events from the blockchain for a specific form.
    Uses the indexed zenbakia field to filter events efficiently.
    Args:
        w3: Web3 instance
        contract: Contract instance
        contract_address: Contract address
        zenbakia: Form number to filter events by (indexed field)
        from_block: Starting block number to search from
    Returns:
        Tuple of (form_created_events, form_updated_events) lists
    """
    print(f"\nRetrieving events for form zenbakia={zenbakia} from block {from_block}...")
    
    # Get the latest block number
    latest_block = w3.eth.block_number
    print(f"  Searching from block {from_block} to block {latest_block}")
    
    try:
        # Use argument_filters to filter by the indexed zenbakia field
        # This is more efficient than retrieving all events and filtering in Python
        argument_filters = {'zenbakia': zenbakia}
        
        # Get FormCreated events filtered by zenbakia
        # Note: web3.py uses snake_case for parameters (from_block, to_block)
        form_created_events = contract.events.FormCreated.get_logs(
            from_block=from_block, 
            to_block=latest_block,
            argument_filters=argument_filters
        )
        
        # Get FormUpdated events filtered by zenbakia
        form_updated_events = contract.events.FormUpdated.get_logs(
            from_block=from_block, 
            to_block=latest_block,
            argument_filters=argument_filters
        )
        
        print(f"  Found {len(form_created_events)} FormCreated events for form {zenbakia}")
        print(f"  Found {len(form_updated_events)} FormUpdated events for form {zenbakia}")
        
        return form_created_events, form_updated_events
    except Exception as e:
        print(f"  Error retrieving events: {e}")
        # Return empty lists if event retrieval fails
        return [], []

def display_events(form_created_events, form_updated_events):
    """
    Display the retrieved events in a formatted way.
    """
    print(f"\n{'='*60}")
    print(f"EVENT LOGS")
    print(f"{'='*60}")
    
    if form_created_events:
        print(f"\nFormCreated Events:")
        for i, event in enumerate(form_created_events, 1):
            print(f"  Event {i}:")
            print(f"    Block: {event.blockNumber}")
            print(f"    Transaction: {event.transactionHash.hex()}")
            print(f"    zenbakia: {event.args.zenbakia}")
            print(f"    datu1: {event.args.datu1}")
            print(f"    datu2: {event.args.datu2}")
    else:
        print(f"\nNo FormCreated events found")
    
    if form_updated_events:
        print(f"\nFormUpdated Events:")
        for i, event in enumerate(form_updated_events, 1):
            print(f"  Event {i}:")
            print(f"    Block: {event.blockNumber}")
            print(f"    Transaction: {event.transactionHash.hex()}")
            print(f"    zenbakia: {event.args.zenbakia}")
            print(f"    datu1: {event.args.datu1}")
            print(f"    datu2: {event.args.datu2}")
    else:
        print(f"\nNo FormUpdated events found")
    
    print(f"{'='*60}")

def main():
    """
    Main function to orchestrate the entire process.
    """
    try:
        # Step 1: Connect to web3 provider
        w3 = connect_to_provider(IP_LIST)
        
        # Step 2: Create a private Ethereum key
        account = create_private_key()
        
        # Step 3: Load contract files
        bytecode, abi = load_contract_files()
        
        # Step 4: Deploy the contract
        contract, contract_address = deploy_contract(w3, account, bytecode, abi)
        
        # Get the block number after deployment to filter events later
        deployment_block = w3.eth.block_number
        
        # Step 5: Create a form
        create_receipt, form_zenbakia = create_form(w3, account, contract, "Sample Data 1", "Sample Data 2")
        print(f"  Total forms: {form_zenbakia}")
        
        # Step 6: Get the form data using the returned form number
        form_data = get_form(contract, form_zenbakia)
        
        # Step 7: Update the form (first time)
        update_form(w3, account, contract, form_zenbakia, "Updated Data 1", "Updated Data 2")
        
        # Step 8: Update the form (second time)
        update_form(w3, account, contract, form_zenbakia, "Final Data 1", "Final Data 2")
        
        # Step 9: Retrieve and display events for the form we created
        form_created_events, form_updated_events = get_events(
            w3, contract, contract_address, 
            zenbakia=form_zenbakia, 
            from_block=deployment_block
        )
        display_events(form_created_events, form_updated_events)
        
        print(f"\n[SUCCESS] All operations completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()

