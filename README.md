# 🌐 DNS over TLS Proxy (DoT)

## 📖 Overview

A simple, secure DNS-over-TLS proxy daemon that listens for DNS queries on TCP port 53 and forwards them to a public DNS-over-TLS resolver. This project helps protect your DNS queries from eavesdropping and tampering.

```
|        |     TCP/53     |     |     TLS/853     |     |
| Client | <------------->| DoT |<--------------->| DNS |
|        | (Unencrypted)  |     |  (Encrypted)    |     |
```

## 🔐 Why DNS over TLS?

By default, DNS queries and responses are sent in plaintext (usually over UDP), making them visible to networks, ISPs, proxies, and other intermediaries. This lack of privacy can compromise security and, in some cases, human rights. Unencrypted DNS makes it easier for governments to censor the Internet and for attackers to monitor users' online behavior.

**DNS over TLS (DoT)** encrypts DNS queries, keeping them private and secure.

## ✨ Features

- 🧠 Listens on TCP port 53 for incoming DNS queries
- 🔁 Forwards queries to a configurable DNS-over-TLS resolver
- 🧵 Multi-threaded: handles multiple clients concurrently
- 🔒 Secure by default: uses system CA certificates and secure TLS settings
- ⚙️ Simple configuration via environment variables
- 📦 Docker support for easy deployment

## 🚀 Getting Started

### ✅ Prerequisites

- 🐧 **Operating System:** Debian 12 (or compatible)
- 🐳 **Docker:** Version 28.2.x or newer

## ⚙️ Usage

### 🏁 Running the Application

> ⚠️ **Note:** Binding to port 53 may require root privileges on some systems. Docker handles this internally, but if running the app without Docker, consider using `CAP_NET_BIND_SERVICE` or redirecting ports.

1. **Build the Docker image:**
   ```
   docker build -t dot-proxy .
   ```

2. **Run the Docker container:**
   ```
   docker run -dt -p 53:53/tcp --rm --name dot-proxy dot-proxy
   ```

### 🧩 Configuration Options

You can configure the proxy using the following environment variables:

| Variable   | Description                                 | Default     |
|------------|---------------------------------------------|-------------|
| `HOST`     | Local address to listen for DNS queries     | 0.0.0.0     |
| `PORT`     | Local port to listen for DNS queries        | 53          |
| `DNS_HOST` | Upstream DNS-over-TLS resolver address      | 1.1.1.1     |
| `DNS_PORT` | Upstream DNS-over-TLS resolver port         | 853         |

#### Example: Listen on Loopback Interface

```
docker run -dt -p 53:53/tcp \
  -e HOST=127.0.0.1 \
  -e PORT=53 --rm --name dot-proxy dot-proxy
```

#### Example: Use Google DNS Resolver

```
docker run -dt -p 53:53/tcp \
  -e DNS_HOST=8.8.8.8 \
  -e DNS_PORT=853 --rm --name dot-proxy dot-proxy
```

## 🧪 Testing

Open two terminals:

- **Terminal 1:** View Docker logs
   ```
   docker logs -f dot-proxy
   ```
- **Terminal 2:** Test DNS resolution using `dig`
   ```
   dig @127.0.0.1 -p 53 google.com +vc
   ```

**Expected Output (Docker logs):**
```
2025-05-15 12:00:00,153 INFO -> TCP server started on ('0.0.0.0', 53)
2025-05-15 12:00:00,153 INFO -> DNS to forward to ('1.1.1.1', 853)
2025-05-15 12:00:00,084 INFO --> Received request from ('172.17.0.1', 50834), BYTES: 53
2025-05-15 12:00:00,133 INFO ---> Connected to ('1.1.1.1', 853), TLS: TLSv1.3
2025-05-15 12:00:00,133 INFO ---> Forwarded request to 1.1.1.1, BYTES: 53
2025-05-15 12:00:00,165 INFO ---> Received response from 1.1.1.1, BYTES: 470
2025-05-15 12:00:00,165 INFO ---> Sent response to ('172.17.0.1', 50834), BYTES: 470
```

**Expected Output (`dig`):**
```
; <<>> DiG 9.18.28-1~deb12u1 <<>> @127.0.0.1 -p 53 google.com +vc
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 10220
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; PAD: (409 bytes)
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		293	IN	A	172.217.18.238

;; Query time: 78 msec
;; SERVER: 127.0.0.1#53(127.0.0.1) (TCP)
;; WHEN: Sun Jun 15 14:56:20 UTC 2025
;; MSG SIZE  rcvd: 468
```

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE)
