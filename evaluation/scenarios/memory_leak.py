import time

def inject(duration_seconds=180, allocation_mb_per_second=5):
    """
    Simulates a slow memory leak to induce memory pressure and paging.
    """
    print(f"[Memory Leak] Simulating leak for {duration_seconds}s...")
    
    leaked_memory = []
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        # Allocate a chunk of memory (1MB = 1024*1024 bytes)
        chunk_size_bytes = allocation_mb_per_second * 1024 * 1024
        try:
            # Create a byte array and append it to the list to prevent garbage collection
            leaked_memory.append(bytearray(chunk_size_bytes))
            print(f"  Total memory leaked: {len(leaked_memory) * allocation_mb_per_second} MB")
        except MemoryError:
            print("MemoryError: Could not allocate more memory. The system is under pressure.")
            break
        
        time.sleep(1)
        
    print(f"[Memory Leak] Injection finished. Total memory consumed: {len(leaked_memory) * allocation_mb_per_second} MB")
    # The 'leaked_memory' list goes out of scope and will be garbage collected.