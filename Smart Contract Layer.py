class SmartContract:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.train_schedules = {}
        self.seat_availability = {}
        self.fare_structure = {}
        
    def register_train(self, train_id, route, seats, fare_per_seat):
        """Register a new train in the system"""
        contract_data = {
            'type': 'train_registration',
            'train_id': train_id,
            'route': route,
            'total_seats': seats,
            'fare_per_seat': fare_per_seat,
            'timestamp': time.time()
        }
        
        self.train_schedules[train_id] = {
            'route': route,
            'total_seats': seats,
            'available_seats': seats,
            'fare_per_seat': fare_per_seat
        }
        
        self.blockchain.add_reservation(contract_data)
        return True
    
    def book_ticket(self, passenger_info, train_id, num_seats, payment_amount):
        """Execute ticket booking smart contract"""
        if train_id not in self.train_schedules:
            return {'status': 'failed', 'reason': 'Train not found'}
        
        train = self.train_schedules[train_id]
        total_fare = train['fare_per_seat'] * num_seats
        
        # Validate booking conditions
        if train['available_seats'] < num_seats:
            return {'status': 'failed', 'reason': 'Insufficient seats'}
        
        if payment_amount < total_fare:
            return {'status': 'failed', 'reason': 'Insufficient payment'}
        
        # Generate unique ticket ID
        ticket_id = hashlib.sha256(
            f"{passenger_info['name']}{train_id}{time.time()}".encode()
        ).hexdigest()[:12]
        
        # Create reservation record
        reservation_data = {
            'type': 'ticket_booking',
            'ticket_id': ticket_id,
            'passenger_info': passenger_info,
            'train_id': train_id,
            'num_seats': num_seats,
            'total_fare': total_fare,
            'booking_time': time.time(),
            'status': 'confirmed'
        }
        
        # Update seat availability
        train['available_seats'] -= num_seats
        
        # Add to blockchain
        self.blockchain.add_reservation(reservation_data)
        
        return {
            'status': 'success',
            'ticket_id': ticket_id,
            'fare_paid': total_fare,
            'remaining_balance': payment_amount - total_fare
        }
    
    def cancel_ticket(self, ticket_id, cancellation_reason):
        """Execute cancellation smart contract with refund logic"""
        # Find ticket in blockchain
        ticket_found = False
        original_reservation = None
        
        for block in self.blockchain.chain:
            for reservation in block.data if isinstance(block.data, list) else [block.data]:
                if (isinstance(reservation, dict) and 
                    reservation.get('ticket_id') == ticket_id):
                    ticket_found = True
                    original_reservation = reservation
                    break
        
        if not ticket_found:
            return {'status': 'failed', 'reason': 'Ticket not found'}
        
        # Calculate refund based on cancellation policy
        booking_time = original_reservation['booking_time']
        current_time = time.time()
        hours_before_travel = (current_time - booking_time) / 3600
        
        # Refund policy
        if hours_before_travel > 24:
            refund_percentage = 0.9  # 90% refund
        elif hours_before_travel > 12:
            refund_percentage = 0.5  # 50% refund
        else:
            refund_percentage = 0.1  # 10% refund
        
        refund_amount = original_reservation['total_fare'] * refund_percentage
        
        # Create cancellation record
        cancellation_data = {
            'type': 'ticket_cancellation',
            'original_ticket_id': ticket_id,
            'cancellation_time': current_time,
            'refund_amount': refund_amount,
            'reason': cancellation_reason
        }
        
        # Restore seat availability
        train_id = original_reservation['train_id']
        if train_id in self.train_schedules:
            self.train_schedules[train_id]['available_seats'] += original_reservation['num_seats']
        
        self.blockchain.add_reservation(cancellation_data)
        
        return {
            'status': 'success',
            'refund_amount': refund_amount,
            'processing_time': '3-5 business days'
        }
