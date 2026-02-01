import time
import sys
from simulator import simulator

def main():
    print("🚀 Starting Transaction Simulator Service...")
    print("Press Ctrl+C to stop.")
    
    try:
        simulator.start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopping...")
        simulator.stop()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
