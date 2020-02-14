# Paste your version of blockchain.py from the client_mining_p
# folder here
# Paste your version of blockchain.py from the basic_block_gp
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.users = []

        # Create the genesis block
        self.new_block(previous_hash="1", proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            # 'id': id,
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block
    
    def new_transaction(self, sender, recipient, amount):
        """
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        
        self.current_transactions.append(transaction)
        
        return self.last_block['index'] + 1
    
    def change_user(self, user, new_user=None):
        
        counter = 0
        if new_user is None:
            return None
            
        for i in self.chain:
            
            for j in i['transactions']:

                if j['recipient'] == user:
                    j['recipient'] = new_user
                    counter+=1
                    
                if j['sender'] == user:
                    j['sender'] = new_user
                    counter+=1
        if user in self.users:
            self.users.remove(user)
            
        self.save_user(new_user)
        
        return counter
    
    def save_user(self, new_user):
        
        if new_user in self.users:
            pass
        
        else:
            self.users.append(new_user)

        with open('ids.txt', "w") as f:
            for L in self.users:
                f.writelines(L+"\n")



    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # TODO: Hash this string using sha256
        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    # def proof_of_work(self, block):
    #     """
    #     Simple Proof of Work Algorithm
    #     Stringify the block and look for a proof.
    #     Loop through possibilities, checking each one against `valid_proof`
    #     in an effort to find a number that is a valid proof
    #     :return: A valid proof for the provided block
    #     """
        
    #     block_string = json.dumps(block, sort_keys=True)
    #     proof = 0
    #     while self.valid_proof(block_string, proof) is False:
    #         proof += 1

    #     return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        block_string = json.dumps(block_string, sort_keys=True)
        print(block_string)
        guess = f'{block_string}{proof}'.encode()
        print(proof)
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(guess_hash)
        return guess_hash[:3] == "000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()
print(blockchain.save_user('SOMETHING'))
# print(blockchain.chain)
# print(blockchain.hash(blockchain.last_block))
@app.route('/')
def user():
    
    return  render_template('base.html', title='Home', wallet="TEST",transaction_history=""), 200  
    
@app.route('/', methods=['POST'])
def wallet():
    user = request.form["user"]

    transaction_history = []
    balance = 0
    for i in blockchain.chain:
        if len(i['transactions']) == 0:
            continue

        for j in i['transactions']:

            if j['recipient'] == user:
                transaction_history.append(str(j['sender'])+": " + str(j['amount']))
                balance += j['amount']
            if j['sender'] == user:
                transaction_history.append(str(j['recipient'])+": " + str(-j['amount']))
                balance -= j['amount']

    return render_template('base.html', title='Home', wallet=balance,
                            transaction_history=transaction_history), 200
    
@app.route('/changed')
def change():
    return  render_template('change.html', title='Home',change_message=""), 200

@app.route('/changed', methods=['POST'])
def changed():
    
    user = request.form["user"]
    new_user = request.form["new_user"]
    message = blockchain.change_user(user, new_user)
    
    if message is None:
        return render_template('change.html', title='Home', 
                           change_message="No New User Filled"), 200
    
    if message == 0:
        change_message = "This name is not registered"
    else:
        change_message = f'Hooray! You name has been changed in {message} different instances'

    return render_template('change.html', title='Home', 
                           change_message=change_message), 200
    

@app.route('/transaction/new', methods=['POST'])
def receive_new_transaction():
    
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in data for k in required):
        response = {'message': "missing values"}
        return jsonify(response), 400
    blockchain.save_user(data['sender'])
    blockchain.save_user(data['recipient'])
    index = blockchain.new_transaction(data['sender'],
                                       data['recipient'],
                                       data['amount'])
    
    response = {'message': f'Transactions will be included in block {index}'}


    
    return jsonify(response), 200

@app.route('/mine', methods=['POST'])
def mine():
    # proof request
    proof_str = request.data.decode("utf-8") # } these 3 lines can be replaced with
    proof_json = json.loads(proof_str) # } data = request.get_json()
    proof = int(proof_json.get('proof')) # } proof = data['proof']
    my_id = proof_json.get('id')
    # print(proof)
    if blockchain.valid_proof(blockchain.last_block, proof) is False:
        response = {'message': 'Error - Invalid Proof'}
        return jsonify(response), 200
    
    # Forge the new Block by adding it to the chain with the proof
    previous_hash = blockchain.hash(blockchain.last_block)
    
    block_index = blockchain.new_transaction("0", my_id, 1)
    
    new_block = blockchain.new_block(proof, previous_hash)
    blockchain.save_user(my_id)
    response = {
        # TODO: Send a JSON response with the new block
        'index': block_index,
        'id': my_id,
        'proof': proof,
        'block': new_block,
        'message': 'New Block Forged',
    }

    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    
    last = blockchain.last_block

    return jsonify(last), 200



@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000)
