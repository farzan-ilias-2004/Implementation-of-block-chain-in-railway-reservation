def display_menu():
    """Display main menu options"""
    print("\n" + "="*50)
    print("    BLOCKCHAIN RAILWAY RESERVATION SYSTEM")
    print("="*50)
    print("1. Register New User")
    print("2. User Login")
    print("3. Admin Panel")
    print("4. Search Trains")
    print("5. Check PNR Status")
    print("6. Validate Blockchain")
    print("7. Exit")
    print("-"*50)

def user_menu(railway_system, username):
    """User-specific menu after login"""
    while True:
        print(f"\n--- Welcome {username} ---")
        print("1. Search & Book Trains")
        print("2. My Bookings")
        print("3. Cancel Ticket")
        print("4. Logout")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            # Search and book trains
            source = input("Enter source station: ")
            destination = input("Enter destination station: ")
            travel_date = input("Enter travel date (YYYY-MM-DD): ")
            
            trains = railway_system.search_trains(source, destination, travel_date)
            
            if trains:
                print("\nAvailable Trains:")
                for i, train in enumerate(trains):
                    print(f"{i+1}. Train ID: {train['train_id']}")
                    print(f"   Route: {' -> '.join(train['route'])}")
                    print(f"   Available Seats: {train['available_seats']}")
                    print(f"   Fare per Seat: ${train['fare_per_seat']}")
                    print()
                
                train_choice = int(input("Select train (number): ")) - 1
                if 0 <= train_choice < len(trains):
                    selected_train = trains[train_choice]
                    num_seats = int(input("Number of seats: "))
                    
                    passenger_details = {
                        'user': username,
                        'name': input("Passenger name: "),
                        'age': int(input("Passenger age: ")),
                        'gender': input("Gender (M/F/O): ")
                    }
                    
                    result = railway_system.make_reservation(
                        username,
                        selected_train['train_id'],
                        num_seats,
                        passenger_details
                    )
                    
                    if result['status'] == 'success':
                        print(f"\n✓ Booking Successful!")
                        print(f"Ticket ID: {result['ticket_id']}")
                        print(f"Amount Paid: ${result['fare_paid']}")
                    else:
                        print(f"✗ Booking Failed: {result['reason']}")
            else:
                print("No trains available for this route.")
        
        elif choice == '2':
            # Show user bookings
            bookings = railway_system.get_user_bookings(username)
            if bookings:
                print("\nYour Bookings:")
                for booking in bookings:
                    print(f"Ticket ID: {booking['ticket_id']}")
                    print(f"Train ID: {booking['train_id']}")
                    print(f"Seats: {booking['num_seats']}")
                    print(f"Total Fare: ${booking['total_fare']}")
                    print(f"Status: {booking['status']}")
                    print("-" * 30)
            else:
                print("No bookings found.")
        
        elif choice == '3':
            # Cancel ticket
            ticket_id = input("Enter Ticket ID to cancel: ")
            reason = input("Cancellation reason: ")
            
            result = railway_system.cancel_reservation(username, ticket_id, reason)
            
            if result['status'] == 'success':
                print(f"✓ Cancellation Successful!")
                print(f"Refund Amount: ${result['refund_amount']}")
                print(f"Processing Time: {result['processing_time']}")
            else:
                print(f"✗ Cancellation Failed: {result['reason']}")
        
        elif choice == '4':
            break

def main():
    """Main application entry point"""
    railway_system = RailwayReservationSystem()
    
    # Initialize with sample trains (admin operation)
    sample_trains = [
        {
            'train_id': 'EXP001',
            'route': ['Mumbai', 'Pune', 'Bangalore'],
            'seats': 100,
            'fare_per_seat': 250
        },
        {
            'train_id': 'RAJ002', 
            'route': ['Delhi', 'Jaipur', 'Mumbai'],
            'seats': 150,
            'fare_per_seat': 300
        }
    ]
    
    for train in sample_trains:
        railway_system.admin_add_train('admin', 'railway_admin_2024', train)
    
    # Mine initial blocks
    railway_system.blockchain.mine_pending_reservations('system')
    
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            # Register new user
            username = input("Enter username: ")
            password = input("Enter password: ")
            name = input("Full name: ")
            email = input("Email: ")
            phone = input("Phone number: ")
            
            personal_info = {
                'name': name,
                'email': email,
                'phone': phone
            }
            
            result = railway_system.register_user(username, password, personal_info)
            print(f"Registration: {result['status']} - {result.get('message', result.get('reason'))}")
        
        elif choice == '2':
            # User login
            username = input("Username: ")
            password = input("Password: ")
            
            if railway_system.authenticate_user(username, password):
                print("✓ Login successful!")
                user_menu(railway_system, username)
            else:
                print("✗ Invalid credentials!")
        
        elif choice == '3':
            # Admin panel
            admin_user = input("Admin username: ")
            admin_pass = input("Admin password: ")
            
            if (admin_user in railway_system.admin_credentials and 
                railway_system.admin_credentials[admin_user] == admin_pass):
                
                print("\n--- Admin Panel ---")
                print("1. Add New Train")
                print("2. View All Trains")
                print("3. View Blockchain Stats")
                
                admin_choice = input("Enter choice: ")
                
                if admin_choice == '1':
                    train_id = input("Train ID: ")
                    route_input = input("Route (comma-separated): ")
                    route = [station.strip() for station in route_input.split(',')]
                    seats = int(input("Total seats: "))
                    fare = float(input("Fare per seat: "))
                    
                    train_details = {
                        'train_id': train_id,
                        'route': route,
                        'seats': seats,
                        'fare_per_seat': fare
                    }
                    
                    railway_system.admin_add_train(admin_user, admin_pass, train_details)
                    railway_system.blockchain.mine_pending_reservations('admin')
                    print("✓ Train added successfully!")
                
                elif admin_choice == '2':
                    print("\nRegistered Trains:")
                    for train_id, details in railway_system.smart_contract.train_schedules.items():
                        print(f"Train ID: {train_id}")
                        print(f"Route: {' -> '.join(details['route'])}")
                        print(f"Total/Available Seats: {details['total_seats']}/{details['available_seats']}")
                        print(f"Fare per Seat: ${details['fare_per_seat']}")
                        print("-" * 40)
                
                elif admin_choice == '3':
                    print(f"\nBlockchain Statistics:")
                    print(f"Total Blocks: {len(railway_system.blockchain.chain)}")
                    print(f"Pending Reservations: {len(railway_system.blockchain.pending_reservations)}")
                    print(f"Mining Difficulty: {railway_system.blockchain.difficulty}")
                    print(f"Chain Valid: {railway_system.validate_blockchain_integrity()}")
            else:
                print("✗ Admin authentication failed!")
        
        elif choice == '4':
            # Search trains (public access)
            source = input("Enter source station: ")
            destination = input("Enter destination station: ")
            travel_date = input("Enter travel date: ")
            
            trains = railway_system.search_trains(source, destination, travel_date)
            
            if trains:
                print("\nAvailable Trains:")
                for train in trains:
                    print(f"Train ID: {train['train_id']}")
                    print(f"Route: {' -> '.join(train['route'])}")
                    print(f"Available Seats: {train['available_seats']}")
                    print(f"Fare per Seat: ${train['fare_per_seat']}")
                    print("-" * 30)
            else:
                print("No trains available for this route.")
        
        elif choice == '5':
            # Check PNR status
            ticket_id = input("Enter Ticket ID: ")
            result = railway_system.check_pnr_status(ticket_id)
            
            if result['status'] == 'found':
                details = result['reservation_details']
                print(f"\n--- Ticket Details ---")
                print(f"Ticket ID: {details['ticket_id']}")
                print(f"Train ID: {details['train_id']}")
                print(f"Passenger: {details['passenger_info']['name']}")
                print(f"Seats: {details['num_seats']}")
                print(f"Total Fare: ${details['total_fare']}")
                print(f"Status: {details['status']}")
                print(f"Booking Time: {datetime.fromtimestamp(details['booking_time'])}")
                print(f"Block Hash: {result['block_hash']}")
            else:
                print("✗ Ticket not found!")
        
        elif choice == '6':
            # Validate blockchain
            is_valid = railway_system.validate_blockchain_integrity()
            print(f"Blockchain Integrity: {'✓ VALID' if is_valid else '✗ INVALID'}")
        
        elif choice == '7':
            print("Thank you for using Blockchain Railway Reservation System!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
