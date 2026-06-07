from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from infrastructure.config.settings import get_settings

_cluster = None
_session = None


def get_cassandra_session():
    global _cluster, _session
    if _session is None:
        settings = get_settings()
        _cluster = Cluster(
            contact_points=settings.cassandra_hosts,
            port=settings.cassandra_port,
            load_balancing_policy=DCAwareRoundRobinPolicy(local_dc="datacenter1"),
        )
        _session = _cluster.connect(settings.cassandra_keyspace)
    return _session


def shutdown_cassandra():
    global _cluster, _session
    if _cluster:
        _cluster.shutdown()
    _cluster = None
    _session = None
