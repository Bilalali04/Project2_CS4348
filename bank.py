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

# Print lock to prevent overlapping output
print_lock = threading.Lock()

def log(actor_type, actor_id, ctx_type, ctx_id, msg):
    if ctx_type is None:
        line = f"{actor_type} {actor_id} []: {msg}"
    else:
        line = f"{actor_type} {actor_id} [{ctx_type} {ctx_id}]: {msg}"
    with print_lock:
        print(line, flush=True)

def teller(tid):
    global customers_served

    log("Teller", tid, None, None, "ready to serve")
    bank_open.wait()

    while True:
        log("Teller", tid, None, None, "waiting for a customer")

        line_mutex.acquire()
        free_tellers.append(tid)
        line_mutex.release()
        teller_available.release()

        customer_arrived[tid].acquire()

        cid = current_customer_id[tid]
        if cid == -1:
            break

        log("Teller", tid, "Customer", cid, "serving a customer")
        log("Teller", tid, "Customer", cid, "asks for transaction")
        teller_asks[tid].release()

        customer_answers[tid].acquire()
        txn = transaction_type[tid]

        if txn == "withdrawal":
            log("Teller", tid, "Customer", cid, "handling withdrawal transaction")
            log("Teller", tid, "Customer", cid, "going to the manager")
            manager_lock.acquire()
            log("Teller", tid, "Customer", cid, "getting manager's permission")
            time.sleep(random.uniform(0.005, 0.030))
            log("Teller", tid, "Customer", cid, "got manager's permission")
            manager_lock.release()
        else:
            log("Teller", tid, "Customer", cid, "handling deposit transaction")

        log("Teller", tid, "Customer", cid, "going to safe")
        safe_lock.acquire()
        log("Teller", tid, "Customer", cid, "enter safe")
        time.sleep(random.uniform(0.010, 0.050))
        log("Teller", tid, "Customer", cid, "leaving safe")
        safe_lock.release()

        log("Teller", tid, "Customer", cid, f"finishes {txn} transaction.")
        log("Teller", tid, "Customer", cid, "wait for customer to leave.")
        transaction_done[tid].release()
        customer_left[tid].acquire()

        with customers_served_lock:
            customers_served += 1
            done = customers_served >= NUM_CUSTOMERS

        if done:
            break

    log("Teller", tid, None, None, "leaving for the day")