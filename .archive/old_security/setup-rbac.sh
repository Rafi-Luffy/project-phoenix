#!/bin/bash
# RBAC Configuration Script for Project Phoenix
# Implements principle of least privilege with role-based access control

set -e

KUBE_NAMESPACE="${1:-phoenix}"
ENVIRONMENT="${2:-production}"

echo "=========================================="
echo "Setting up RBAC for Project Phoenix"
echo "Namespace: $KUBE_NAMESPACE"
echo "Environment: $ENVIRONMENT"
echo "=========================================="

# Create namespace if it doesn't exist
kubectl create namespace "$KUBE_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Label namespace
kubectl label namespace "$KUBE_NAMESPACE" \
    environment="$ENVIRONMENT" \
    monitoring=enabled \
    --overwrite

echo ""
echo "Creating ServiceAccounts..."

# Create service accounts
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: phoenix-app
  namespace: $KUBE_NAMESPACE

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: phoenix-readonly
  namespace: $KUBE_NAMESPACE

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: phoenix-admin
  namespace: $KUBE_NAMESPACE
EOF

echo "Creating Roles..."

# Create roles for different access levels
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: phoenix-app-role
  namespace: $KUBE_NAMESPACE
rules:
# Pod management
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]

# ConfigMap and Secret reading
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
  resourceNames: ["phoenix-secrets", "database-credentials"]

# Service and Endpoint discovery
- apiGroups: [""]
  resources: ["services", "endpoints"]
  verbs: ["get", "list", "watch"]

# Events
- apiGroups: [""]
  resources: ["events"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: phoenix-readonly-role
  namespace: $KUBE_NAMESPACE
rules:
# Read-only access
- apiGroups: [""]
  resources: ["pods", "pods/log", "services", "endpoints", "events"]
  verbs: ["get", "list", "watch"]

- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch"]

- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: phoenix-admin-role
  namespace: $KUBE_NAMESPACE
rules:
# Admin access - all verbs on all resources
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
EOF

echo "Creating RoleBindings..."

# Create role bindings
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: phoenix-app-binding
  namespace: $KUBE_NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: phoenix-app-role
subjects:
- kind: ServiceAccount
  name: phoenix-app
  namespace: $KUBE_NAMESPACE

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: phoenix-readonly-binding
  namespace: $KUBE_NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: phoenix-readonly-role
subjects:
- kind: ServiceAccount
  name: phoenix-readonly
  namespace: $KUBE_NAMESPACE

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: phoenix-admin-binding
  namespace: $KUBE_NAMESPACE
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: phoenix-admin-role
subjects:
- kind: ServiceAccount
  name: phoenix-admin
  namespace: $KUBE_NAMESPACE
EOF

echo "Creating ClusterRoles..."

# Create cluster-level roles
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: phoenix-metrics-reader
rules:
- apiGroups: [""]
  resources: ["nodes/metrics", "nodes/proxy"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: phoenix-metrics-reader-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: phoenix-metrics-reader
subjects:
- kind: ServiceAccount
  name: phoenix-app
  namespace: $KUBE_NAMESPACE
EOF

echo "Creating NetworkPolicies..."

# Apply network policies
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: phoenix-network-policy
  namespace: $KUBE_NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: phoenix-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
EOF

echo "Creating Resource Quotas..."

# Create resource quotas
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: phoenix-quota
  namespace: $KUBE_NAMESPACE
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    pods: "100"
    services: "10"
    services.nodeports: "5"
    configmaps: "20"
    secrets: "20"
    persistentvolumeclaims: "10"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: phoenix-limits
  namespace: $KUBE_NAMESPACE
spec:
  limits:
  - max:
      cpu: "2"
      memory: "4Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    type: Container
  - max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "200m"
      memory: "256Mi"
    type: Pod
EOF

echo ""
echo "=========================================="
echo "RBAC Configuration Complete!"
echo "=========================================="
echo ""
echo "Service Accounts Created:"
kubectl get sa -n "$KUBE_NAMESPACE"
echo ""
echo "Roles Created:"
kubectl get roles -n "$KUBE_NAMESPACE"
echo ""
echo "Role Bindings Created:"
kubectl get rolebindings -n "$KUBE_NAMESPACE"
echo ""
echo "=========================================="
