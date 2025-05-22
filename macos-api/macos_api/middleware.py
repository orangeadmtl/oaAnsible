import ipaddress
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Assuming TAILSCALE_SUBNET is imported from .core.config
from .core.config import TAILSCALE_SUBNET

logger = logging.getLogger(__name__)


class TailscaleSubnetMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, tailscale_subnet_str=TAILSCALE_SUBNET):  # Renamed to avoid conflict
        super().__init__(app)
        try:
            # strict=False allows host IPs within the network definition itself
            self.tailscale_subnet = ipaddress.ip_network(tailscale_subnet_str, strict=False)
            logger.info(f"TailscaleSubnetMiddleware initialized with subnet: {self.tailscale_subnet}")
        except ValueError as e:
            logger.error(f"Invalid TAILSCALE_SUBNET format: {tailscale_subnet_str}. Error: {e}")
            # Fallback to a very restrictive default if config is bad to prevent insecure startup.
            # This effectively blocks all non-localhost traffic if TAILSCALE_SUBNET is misconfigured.
            self.tailscale_subnet = ipaddress.ip_network("0.0.0.0/32", strict=False)
            logger.warning(f"TAILSCALE_SUBNET '{tailscale_subnet_str}' is invalid. Middleware will be extremely restrictive.")

    async def dispatch(self, request: Request, call_next):
        client_ip_str = request.client.host

        try:
            client_ip_obj = ipaddress.ip_address(client_ip_str)
        except ValueError:
            # This case handles if request.client.host is not a valid IP string
            logger.error(f"Invalid client IP format: {client_ip_str} in TailscaleSubnetMiddleware")
            raise HTTPException(status_code=400, detail="Invalid client IP address format")

        is_localhost = client_ip_obj.is_loopback  # Correctly checks for 127.0.0.1, ::1

        if request.method == "POST":
            # For POST requests, client IP MUST be in the Tailscale subnet.
            # Loopback/localhost is explicitly not sufficient here as per "from a Tailscale IP source".
            if client_ip_obj not in self.tailscale_subnet:
                logger.warning(f"POST Access DENIED for IP {client_ip_str} (not in Tailscale subnet {self.tailscale_subnet})")
                raise HTTPException(status_code=403, detail="Access denied: POST requests must originate from the Tailscale network.")
            logger.debug(f"POST Access ALLOWED for IP {client_ip_str} (in Tailscale subnet)")
        else:  # For GET, OPTIONS, HEAD, etc.
            if is_localhost:
                logger.debug(f"{request.method} Access ALLOWED for IP {client_ip_str} (localhost)")
            elif client_ip_obj not in self.tailscale_subnet:
                logger.warning(
                    f"{request.method} Access DENIED for IP {client_ip_str} (not localhost and not in Tailscale subnet {self.tailscale_subnet})"
                )
                raise HTTPException(status_code=403, detail="Access denied: Request must originate from localhost or the Tailscale network.")
            else:
                logger.debug(f"{request.method} Access ALLOWED for IP {client_ip_str} (in Tailscale subnet)")

        return await call_next(request)
