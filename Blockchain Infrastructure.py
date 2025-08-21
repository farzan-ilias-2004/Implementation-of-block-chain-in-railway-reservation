import hashlib
import json
import time
from datetime import datetime
import random

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Railway reservation data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """Proof of Work mining with adjustable difficulty"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

class RailwayBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_reservations = []
        self.mining_reward = 100
        
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        return Block(0, time.time(), "Genesis Block", "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_reservation(self, reservation):
        """Add reservation to pending transactions"""
        self.pending_reservations.append(reservation)
    
    def mine_pending_reservations(self, mining_reward_address):
        """Mine pending reservations into a new block"""
        reward_reservation = {
            'type': 'mining_reward',
            'amount': self.mining_reward,
            'to': mining_reward_address
        }
        self.pending_reservations.append(reward_reservation)
        
        block = Block(
            len(self.chain),
            time.time(),
            self.pending_reservations,
            self.get_latest_block().hash
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_reservations = []
    
    def is_chain_valid(self):
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
