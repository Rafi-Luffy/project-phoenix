# HashiCorp Vault Configuration for Project Phoenix
# Production-ready Vault setup with high availability and disaster recovery

storage "raft" {
  path = "/vault/data"
  node_id = "vault_node_1"
  performance_multiplier = 8
  trailing_logs = 10000
  snapshot_interval = "30s"
  snapshot_delay = "5s"
  retry_join {
    leader_api_addr = "https://vault-1.vault.service.consul:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-2.vault.service.consul:8200"
  }
  retry_join {
    leader_api_addr = "https://vault-3.vault.service.consul:8200"
  }
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/config/tls/vault.crt"
  tls_key_file  = "/vault/config/tls/vault.key"
  tls_min_version = "tls12"
  tls_cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"
  ]
  telemetry {
    unauthenticated_metrics_access = false
  }
}

listener "unix" {
  address = "/vault/run/socket"
  tls_disable = true
}

# Service Registration (Consul)
service_registration "consul" {
  address = "consul:8500"

  check {
    id       = "vault-sealed-status"
    name     = "Vault Sealed Status"
    notes    = "Checks whether Vault is sealed or unsealed. A sealed Vault cannot be used, so alerts should be triggered if this check fails."
    script   = "curl -sS http://127.0.0.1:8200/v1/sys/seal-status | jq '.sealed' | grep 'false' >/dev/null"
    interval = "10s"
    timeout  = "5s"
  }

  check {
    id       = "vault-ha-status"
    name     = "Vault HA Status"
    notes    = "Checks the HA status of Vault. This check ensures that Vault is not in standby mode."
    script   = "curl -sS http://127.0.0.1:8200/v1/sys/ha-status | jq '.is_self' | grep 'true' >/dev/null"
    interval = "10s"
    timeout  = "5s"
  }
}

# Telemetry and monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname          = false
  enable_utf8               = true
}

api_addr = "https://vault:8200"
cluster_addr = "https://vault:8201"
ui = true

# Logging
log_level = "info"
log_format = "json"

# Plugin directory
plugin_directory = "/vault/plugins"

# Global defaults
max_lease_ttl = "87600h"
default_lease_ttl = "87600h"

# High Availability Replication
ha_storage "raft" {
  path = "/vault/data"
  node_id = "vault_node_1"
}

# Performance Standby
replication {
  resolver_discover_servers = true
  token_polled_interval      = "10s"
  log_health_states          = true
}

# Clustering
cluster {
  disabled = false
  addr = "0.0.0.0:8201"
  server_name = "vault.service.consul"
  cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
  ]
  tls_min_version = "tls12"
}
