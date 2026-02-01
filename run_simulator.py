import time
import sys
from simulator import simulator

def main():
    print("🚀 Starting Transaction Simulator Service...")
    print("⏱️  Auto-stop set to 2 minutes.")
    
    # Auto-stop configuration
    DURATION_SECONDS = 120
    start_time = time.time()
    
    try:
        simulator.start()
        
        while True:
            elapsed = time.time() - start_time
            remaining = DURATION_SECONDS - elapsed
            
            if remaining <= 0:
                print(f"\n🛑 Timer reached {DURATION_SECONDS}s. Stopping simulator automatically.")
                break
            
            # Sleep specifically to be responsive but not busy wait
            time.sleep(min(1, remaining))
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator manually stopped.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
    finally:
        simulator.stop()
        print("✅ Simulator shutdown complete.")
        sys.exit(0)

if __name__ == "__main__":
    main()
