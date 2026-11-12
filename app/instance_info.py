import os
import socket
import urllib.request

METADATA_BASE = "http://169.254.169.254/latest"


def get_instance_info():
    info = {"instance_id": "local-development", "az": "local", "hostname": socket.gethostname()}
    # Only query metadata on EC2; don't add an IMDSv1 fallback.
    if os.getenv("AWS_EXECUTION_ENV") is None and os.getenv("RUNNING_ON_EC2") != "true":
        return info
    try:
        token_request = urllib.request.Request(
            f"{METADATA_BASE}/api/token",
            data=b"",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        )
        with urllib.request.urlopen(token_request, timeout=1) as response:
            token = response.read().decode()
        for key, path in (("instance_id", "instance-id"), ("az", "placement/availability-zone")):
            request = urllib.request.Request(
                f"{METADATA_BASE}/meta-data/{path}",
                headers={"X-aws-ec2-metadata-token": token},
            )
            with urllib.request.urlopen(request, timeout=1) as response:
                info[key] = response.read().decode()
    except (OSError, ValueError):
        info["instance_id"] = "metadata-unavailable"
        info["az"] = "unknown"
    return info
