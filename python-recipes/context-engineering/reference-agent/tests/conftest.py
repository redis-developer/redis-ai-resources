import os
import time

import pytest
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="session")
def redis_stack_url():
    """Start a Redis 8 container (modules built-in) and yield REDIS_URL."""
    image = os.getenv("TEST_REDIS_IMAGE", "redis:8.2.1")
    with DockerContainer(image) as c:
        c.with_exposed_ports(6379)
        c.start()
        host = c.get_container_host_ip()
        port = int(c.get_exposed_port(6379))
        url = f"redis://{host}:{port}"
        # Tiny wait for readiness
        time.sleep(1.0)
        yield url
