import docker

def get_running_containers():
    """Returns a dict of running containers {cgroup_id: name}."""
    client = docker.from_env()
    containers = {}
    for container in client.containers.list():
        try:
            # This is a simplified way to get a cgroup-like ID.
            # A real implementation would parse /proc/self/cgroup.
            cgroup_id = container.id[:12] # Use a portion of the container ID
            containers[cgroup_id] = container.name
        except Exception:
            continue
    return containers