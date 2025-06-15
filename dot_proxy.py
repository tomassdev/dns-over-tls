import os
import socket
import socketserver
import ssl
import logging
from typing import Tuple, Type, cast

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ProxyTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """A threaded TCP server that forwards DNS requests over TLS."""

    allow_reuse_address = True

    def __init__(
        self,
        server_address: Tuple[str, int],
        resolver_address: Tuple[str, int],
        request_handler: Type[socketserver.BaseRequestHandler],
    ):
        super().__init__(server_address, request_handler)
        self.resolver_address = resolver_address


class TCPHandler(socketserver.BaseRequestHandler):
    """Handles incoming TCP requests and forwards them over TLS to a DNS resolver."""

    def handle(self) -> None:
        try:
            request = self._receive_request()
            if request:
                response = self._forward_to_resolver(request)
                self._send_response(response)
        except Exception as e:
            logging.exception(f"Error handling request from {self.client_address}: {e}")

    def _receive_request(self) -> bytes:
        request = self.request.recv(4096)
        logging.info(
            f"--> Received request from {self.client_address}, BYTES: {len(request)}"
        )
        return request

    def _send_response(self, response: bytes) -> None:
        self.request.sendall(response)
        logging.info(
            f"---> Sent response to {self.client_address}, BYTES: {len(response)}"
        )

    def _create_tls_socket(self, host: str) -> ssl.SSLSocket:
        ssl_context = ssl.create_default_context()
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tls_sock = ssl_context.wrap_socket(tcp_sock, server_hostname=host)
        tls_sock.settimeout(5)
        return tls_sock

    def _forward_to_resolver(self, request: bytes) -> bytes:
        proxy_server = cast(ProxyTCPServer, self.server)
        host, port = proxy_server.resolver_address

        tls_sock = self._create_tls_socket(host)

        tls_sock.connect((host, port))
        logging.info(f"---> Connected to {(host, port)}, TLS: {tls_sock.version()}")

        tls_sock.sendall(request)
        logging.info(f"---> Forwarded request to {host}, BYTES: {len(request)}")

        response = tls_sock.recv(4096)
        logging.info(f"---> Received response from {host}, BYTES: {len(response)}")

        tls_sock.close()
        return response


if __name__ == "__main__":
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "53"))
    DNS_HOST = os.environ.get("DNS_HOST", "1.1.1.1")
    DNS_PORT = int(os.environ.get("DNS_PORT", "853"))

    with ProxyTCPServer((HOST, PORT), (DNS_HOST, DNS_PORT), TCPHandler) as server:
        logging.info(f"-> TCP server started on {(HOST, PORT)}")
        logging.info(f"-> DNS to forward to {(DNS_HOST, DNS_PORT)}")
        server.serve_forever()
