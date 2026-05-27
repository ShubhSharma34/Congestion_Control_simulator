import time

# 🔧 USER INPUT
users = int(input("Enter number of users (shows running): "))
capacity = int(input("Enter network capacity (packets/sec): "))
queue_size = int(input("Enter router queue size: "))

# 🧠 Decide algorithm
load = users / capacity

if load < 1:
    algo = "Tahoe"
elif load < 2:
    algo = "Reno"
else:
    algo = "New Reno"

print("\n🎯 Suggested Algorithm:", algo)
print("\n🎬 Starting LIVE Simulation...\n")

# Variables
cwnd = 1
ssthresh = 8
queue = 0

for t in range(1, 25):
    print("="*40)
    print(f"⏱️ Time Step {t}")

    sent = cwnd
    print(f"📤 Sending packets: {sent}")

    # Check congestion
    if queue + sent > queue_size:
        print("🚨 CONGESTION! Packet Loss Occurred")

        if algo == "Tahoe":
            ssthresh = max(cwnd // 2, 1)
            cwnd = 1
            print("👉 Tahoe: cwnd RESET to 1")

        elif algo == "Reno":
            ssthresh = max(cwnd // 2, 1)
            cwnd = ssthresh
            print("👉 Reno: cwnd reduced to half")

        elif algo == "New Reno":
            ssthresh = max(cwnd // 2, 1)
            cwnd = ssthresh + 1
            print("👉 New Reno: faster recovery")

        queue = queue_size

    else:
        queue += sent

        if cwnd < ssthresh:
            cwnd *= 2
            print("🚀 Slow Start → cwnd doubled")
        else:
            cwnd += 1
            print("📈 Congestion Avoidance → cwnd increased")

    # Process queue
    processed = min(queue, capacity)
    queue -= processed

    print(f"📥 Processed: {processed}")
    print(f"📦 Queue: {queue}/{queue_size}")
    print(f"📊 cwnd: {cwnd}")

    # OTT interpretation
    if queue > queue_size * 0.7:
        print("🎬 Streaming: BUFFERING 😣")
    elif queue > queue_size * 0.3:
        print("🎬 Streaming: 720p (stable)")
    else:
        print("🎬 Streaming: 1080p (smooth)")

    time.sleep(0.7)

print("\n✅ Simulation Complete")