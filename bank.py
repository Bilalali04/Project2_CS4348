import threading
import random
import time

NUM_TELLERS = 3
NUM_CUSTOMERS = 50

# Manager: only 1 teller at a time
manager_lock = threading.Semaphore(1)

# Safe: only 2 tellers at a time
safe_lock = threading.Semaphore(2)

# Door: only 2 customers entering at a time
door_lock = threading.Semaphore(2)

# Bank open barrier: main waits here until all 3 tellers are ready
bank_open = threading.Barrier(NUM_TELLERS + 1)

# Line management
line_mutex       = threading.Semaphore(1)
free_tellers     = []
teller_available = threading.Semaphore(0)

# Per-teller synchronization semaphores
customer_arrived = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
teller_asks      = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_answers = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
transaction_done = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_left    = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]

# Per-teller shared data
current_customer_id = [-1]   * NUM_TELLERS
transaction_type    = [None] * NUM_TELLERS

# Shutdown tracking
customers_served      = 0
customers_served_lock = threading.Lock()