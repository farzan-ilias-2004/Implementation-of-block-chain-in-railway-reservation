class RailwayReservationSystem:
    def __init__(self):
        self.blockchain = RailwayBlockchain()
        self.smart_contract = SmartContract(self.blockchain)
        self.users = {}
        self.admin_credentials = {'admin': 'railway_admin_2024'}
        
    def register_user(self, username, password, personal_info):
        """Register new user in the system"""
        if username in self.users:
            return {'status': 'failed', 'reason': 'User already exists'}
        
        user_data = {
            'username': username,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'personal_info': personal_info,
            'registration_time': time.time()
        }
        
        self.users[username] = user_data
        
        # Record user registration on blockchain
        registration_record = {
            'type': 'user_registration',
            'username': username,
            'registration_time': time.time()
        }
        
        self.blockchain.add_reservation(registration_record)
        return {'status': 'success', 'message': 'User registered successfully'}
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        if username in self.users:
            stored_password = self.users[username]['password']
            provided_password = hashlib.sha256(password.encode()).hexdigest()
            return stored_password == provided_password
        return False
    
    def admin_add_train(self, admin_username, admin_password, train_details):
        """Admin function to add new trains"""
        if (admin_username in self.admin_credentials and 
            self.admin_credentials[admin_username] == admin_password):
            
            return self.smart_contract.register_train(
                train_details['train_id'],
                train_details['route'],
                train_details['seats'],
                train_details['fare_per_seat']
            )
        
        return {'status': 'failed', 'reason': 'Admin authentication failed'}
    
    def search_trains(self, source, destination, travel_date):
        """Search available trains for given route"""
        available_trains = []
        
        for train_id, details in self.smart_contract.train_schedules.items():
            route = details['route']
            if source in route and destination in route:
                # Check if source comes before destination in route
                source_index = route.index(source)
                dest_index = route.index(destination)
                
                if source_index < dest_index:
                    available_trains.append({
                        'train_id': train_id,
                        'route': route,
                        'available_seats': details['available_seats'],
                        'fare_per_seat': details['fare_per_seat']
                    })
        
        return available_trains
    
    def make_reservation(self, username, train_id, num_seats, passenger_details):
        """Make a new reservation"""
        if username not in self.users:
            return {'status': 'failed', 'reason': 'User not registered'}
        
        # Simulate payment (in real implementation, integrate with payment gateway)
        train_info = self.smart_contract.train_schedules.get(train_id)
        if not train_info:
            return {'status': 'failed', 'reason': 'Invalid train'}
        
        total_amount = train_info['fare_per_seat'] * num_seats
        
        # Execute smart contract
        result = self.smart_contract.book_ticket(
            passenger_details,
            train_id,
            num_seats,
            total_amount
        )
        
        # Mine the block after successful booking
        if result['status'] == 'success':
            self.blockchain.mine_pending_reservations(username)
        
        return result
    
    def check_pnr_status(self, ticket_id):
        """Check reservation status using ticket ID"""
        for block in self.blockchain.chain:
            block_data = block.data if isinstance(block.data, list) else [block.data]
            for reservation in block_data:
                if (isinstance(reservation, dict) and 
                    reservation.get('ticket_id') == ticket_id):
                    return {
                        'status': 'found',
                        'reservation_details': reservation,
                        'block_hash': block.hash,
                        'block_timestamp': block.timestamp
                    }
        
        return {'status': 'not_found', 'message': 'Invalid ticket ID'}
    
    def cancel_reservation(self, username, ticket_id, reason):
        """Cancel existing reservation"""
        if username not in self.users:
            return {'status': 'failed', 'reason': 'User not registered'}
        
        result = self.smart_contract.cancel_ticket(ticket_id, reason)
        
        # Mine the cancellation block
        if result['status'] == 'success':
            self.blockchain.mine_pending_reservations(username)
        
        return result
    
    def get_user_bookings(self, username):
        """Get all bookings for a specific user"""
        user_bookings = []
        
        for block in self.blockchain.chain:
            block_data = block.data if isinstance(block.data, list) else [block.data]
            for reservation in block_data:
                if (isinstance(reservation, dict) and 
                    reservation.get('type') == 'ticket_booking' and
                    reservation.get('passenger_info', {}).get('user') == username):
                    user_bookings.append(reservation)
        
        return user_bookings
    
    def validate_blockchain_integrity(self):
        """Validate the entire blockchain for tampering"""
        return self.blockchain.is_chain_valid()
