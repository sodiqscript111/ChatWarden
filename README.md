# ChatWarden

**High-Performance Real-Time Content Moderation Engine**

ChatWarden is a modular, high-throughput moderation infrastructure designed for live-streaming environments (Twitch, Kick, YouTube Live). Built on an asynchronous Python architecture, it leverages **Redis** for distributed state management, **Sliding Window** algorithms for precise rate limiting, and **Probabilistic Cuckoo Filters** for memory-efficient, O(1) keyword blocking. It ensures sub-millisecond latency for abuse detection at scale.

## 🚀 Key Features

*   **Real-time Message Filtering**: Instantaneously blocks hate speech, spam, and toxic content using a hybrid approach of exact matching and probabilistic data structures.
*   **High-Precision Rate Limiting**: Implements a **Sliding Window Log** algorithm (via Redis Sorted Sets) to strictly enforce message velocity limits (e.g., 5 messages per 10 seconds) with millisecond accuracy, preventing "ban evasion" common in fixed-window systems.
*   **Distributed State Management**: Fully stateless application logic backed by Redis, allowing for horizontal scaling to handle viral traffic spikes.
*   **Cuckoo Filter Blocking**: Uses Cuckoo Filters for user blocking and banned word detection. Cuckoo filters offer O(1) lookups and are significantly more space-efficient than standard Bloom filters, while also supporting deletions (which Bloom filters do not).
*   **Shadow Banning & Muting**: granular control over user punishments.
*   **Asynchronous Core**: Built with `asyncio` to handle thousands of concurrent connections without blocking.

## 🏗️ Architecture

ChatWarden follows a **Modular Monolith** architecture. This allows for the simplicity of a single codebase while maintaining strict boundaries between domains (Moderation, User Management, Messaging), making it easy to decompose into microservices if scale requires it in the future.

### Technical Decisions

#### 1. Redis for Everything
We explicitly chose Redis not just for caching, but as the primary proper store for ephemeral state (rate limits, active chat sessions).
*   **Sorted Sets (ZSET)**: Used for the Sliding Window Rate Limiter. The score is the timestamp; the member is a UUID. This allows us to `ZREMRANGEBYSCORE` (remove old entries) and `ZCARD` (count current attempts) in a single atomic pipeline.
*   **Redis Stack / Bloom**: We allow progressive enhancement. If `RedisBloom` is available, we use the native Cuckoo Filter module. If not, the system gracefully degrades to standard Redis Sets.

#### 2. Cuckoo Filters vs. Bloom Filters
We chose Cuckoo Filters because, unlike Bloom filters:
*   They support **deleting** items (crucial for unbanning users or removing words from the blocklist).
*   They provide higher space efficiency for the same false positive rate.

#### 3. Python Asyncio
The I/O-bound nature of chat (waiting for network, waiting for DB) makes Python's `asyncio` the perfect candidate. We use `uvicorn` as the ASGI worker to handle high concurrency with minimal resource overhead.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.11+
*   Redis (6.2+ recommended; Redis Stack desired for Cuckoo Filter support)

### Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sodiqscript111/ChatWarden.git
    cd ChatWarden
    ```

2.  **Set up the environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file:
    ```env
    REDIS_URL=redis://localhost:6379/0
    RATE_LIMIT_WINDOW=10
    RATE_LIMIT_MAX_OFFENSES=5
    ```

4.  **Run the System:**
    ```bash
    uvicorn src.main:app --reload
    ```

## 🧪 Testing

We include a comprehensive stress test suite to verify the race-condition handling of the rate limiter.

```bash
python -m src.stress_test
```

## 🤝 Contributing
Contributions are welcome! Please ensure any PRs targeting the core moderation logic include updated stress tests.

## 📜 License
MIT
