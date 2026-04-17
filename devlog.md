# Dev Log - CS4348 Project 2: Bank Simulation

---

## 2026-04-16 — Initial Entry

### Thoughts so far

The project is a multi-threaded bank simulation. There are 3 teller threads and 50 customer threads. The core challenge is synchronization: tellers and customers must coordinate in a specific order, and shared resources (the manager and the safe) need to be protected.

Key constraints from the spec:
- Bank does not open until all 3 tellers are ready.
- The door allows only 2 customers to enter at a time.
- Only 2 tellers may be in the safe at once.
- Only 1 teller may talk to the manager at a time.
- A teller must wait for the customer to leave before serving the next.
- Customers must wait in line if no teller is free.

### Plan for this session

Implement the full simulation in Python using `threading.Semaphore`.

Semaphore design:
- `bank_open`: a `threading.Barrier(4)` — 3 tellers + main thread all wait here; main releases customers only after all tellers are ready.
- `door_lock`: Semaphore(2) — limits concurrent entry to 2.
- `manager_lock`: Semaphore(1) — mutual exclusion on manager.
- `safe_lock`: Semaphore(2) — allows up to 2 tellers in safe.
- `teller_available`: Semaphore(0), counting semaphore incremented when a teller is free.
- `free_tellers`: a list (protected by `line_mutex`) of available teller ids.
- Per-teller semaphores: `customer_arrived`, `teller_asks`, `customer_answers`, `transaction_done`, `customer_left` — these sequence the teller/customer handshake.

---

## 2026-04-16 — Session 1: Constants and Semaphores

### Thoughts so far

No new thoughts since the initial entry. Moving into implementation.

### Plan for this session

Set up the skeleton of bank.py. Define the thread counts, all semaphores, and shared variables. No thread logic yet, just the foundation everything else will build on.

---

## 2026-04-16 — Session 2: Print Helper

### Thoughts so far

Now that the shared variables are in place, I need a way to print output in the correct format before writing any thread logic. All output follows the pattern `THREAD_TYPE ID [THREAD_TYPE ID]: MSG` so it makes sense to centralize this in a helper function.

### Plan for this session

Add the `log()` function and a `print_lock` to make sure print statements from different threads don't overlap.