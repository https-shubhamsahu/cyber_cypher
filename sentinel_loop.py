import time
import agent_engine
import sys

def main():
    print("🚀 Starting Sentinel AI Autonomous Loop...")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            # Run the agent cycle
            agent_engine.run_agent_cycle()
            
            # Wait for 60 seconds to respect API Rate Limits (free tier)
            print("\nComputing next cycle in 60 seconds...", flush=True)
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Sentinel AI stopping...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
