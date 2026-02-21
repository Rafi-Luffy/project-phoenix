import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft, Copy, Check, Server, Scale, Shield, Activity } from "lucide-react";
import { useState } from "react";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={copy}
      className="p-2 rounded-lg hover:bg-muted/50 transition-colors text-muted-foreground hover:text-foreground"
    >
      {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

const KubernetesLogo = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="#326CE5">
    <path d="M10.204 14.35l.007.01-.999 2.413a5.171 5.171 0 01-2.075-2.597l2.578-.437.004.005a.44.44 0 01.485.606zm-.833-2.129a.44.44 0 00.173-.756l.002-.011L7.585 9.7a5.143 5.143 0 00-.73 3.255l2.514-.725.002-.009zm1.145-1.98a.44.44 0 00.699-.337l-.01-.002.3-2.627a5.07 5.07 0 00-2.85 1.534l1.86 1.43.001.002zm8.143-.576a5.167 5.167 0 00-.73-3.255l-1.963 1.754.002.011a.44.44 0 00.173.756l.002.01 2.514.724h.002zM12 16.018c-.14 0-.28.014-.417.04l-.007.007-1.093 2.341a5.158 5.158 0 002.985.029l-1.053-2.376-.007-.007A1.52 1.52 0 0012 16.018zm-.182-3.285a.44.44 0 00-.609-.147.44.44 0 00-.147.609l1.063 1.846a1.49 1.49 0 00-.307-2.308z"/>
  </svg>
);

const features = [
  {
    icon: Server,
    title: "Helm Charts",
    description: "Production-ready Helm charts for easy deployment"
  },
  {
    icon: Scale,
    title: "Auto-Scaling",
    description: "HPA and VPA for dynamic resource allocation"
  },
  {
    icon: Shield,
    title: "Secrets & RBAC",
    description: "Secure credential management with Kubernetes secrets"
  },
  {
    icon: Activity,
    title: "Health Probes",
    description: "Liveness and readiness probes for reliability"
  }
];

const helmInstallExample = `# Add Phoenix Helm repository
helm repo add phoenix https://charts.phoenix.dev
helm repo update

# Install Phoenix agents
helm install phoenix-agents phoenix/phoenix-agent \\
  --namespace phoenix \\
  --create-namespace \\
  --set apiKey=$PHOENIX_API_KEY \\
  --set replicas=3`;

const deploymentExample = `apiVersion: apps/v1
kind: Deployment
metadata:
  name: phoenix-agent
  namespace: phoenix
  labels:
    app: phoenix-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: phoenix-agent
  template:
    metadata:
      labels:
        app: phoenix-agent
    spec:
      containers:
        - name: agent
          image: phoenixai/agent:1.4.2
          ports:
            - containerPort: 8080
          env:
            - name: PHOENIX_API_KEY
              valueFrom:
                secretKeyRef:
                  name: phoenix-secrets
                  key: api-key
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: phoenix-secrets
                  key: openai-key
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10`;

const serviceExample = `apiVersion: v1
kind: Service
metadata:
  name: phoenix-agent-service
  namespace: phoenix
spec:
  selector:
    app: phoenix-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phoenix-agent-ingress
  namespace: phoenix
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - agents.yourdomain.com
      secretName: phoenix-tls
  rules:
    - host: agents.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: phoenix-agent-service
                port:
                  number: 80`;

const hpaExample = `apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: phoenix-agent-hpa
  namespace: phoenix
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: phoenix-agent
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60`;

const secretsExample = `apiVersion: v1
kind: Secret
metadata:
  name: phoenix-secrets
  namespace: phoenix
type: Opaque
stringData:
  api-key: "your-phoenix-api-key"
  openai-key: "your-openai-api-key"
---
# External Secrets Operator integration
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: phoenix-external-secrets
  namespace: phoenix
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: phoenix-secrets
  data:
    - secretKey: api-key
      remoteRef:
        key: phoenix/production
        property: api_key
    - secretKey: openai-key
      remoteRef:
        key: phoenix/production
        property: openai_key`;

export default function KubernetesIntegration() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Header */}
      <section className="pt-32 pb-12 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(50,108,229,0.15),transparent_60%)]" />
        
        <div className="container mx-auto max-w-5xl relative z-10">
          <Link 
            to="/docs/sdk"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to SDK Reference
          </Link>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex items-center gap-6 mb-6"
          >
            <KubernetesLogo />
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                Kubernetes Integration
              </h1>
              <p className="text-lg text-muted-foreground mt-2">
                Production-grade orchestration for Phoenix agents at scale
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="p-4 rounded-xl bg-muted/20 border border-border"
              >
                <feature.icon className="w-8 h-8 text-[#326CE5] mb-3" />
                <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Helm Install */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Quick Start with Helm</h2>
          <p className="text-muted-foreground mb-6">
            Deploy Phoenix agents in seconds using our official Helm chart.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">Terminal</span>
              <CopyButton text={helmInstallExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{helmInstallExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Deployment */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Deployment Manifest</h2>
          <p className="text-muted-foreground mb-6">
            Full deployment configuration with health probes and resource limits.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">deployment.yaml</span>
              <CopyButton text={deploymentExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{deploymentExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Service & Ingress */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Service and Ingress</h2>
          <p className="text-muted-foreground mb-6">
            Expose your agents with TLS termination and load balancing.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">service.yaml</span>
              <CopyButton text={serviceExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{serviceExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* HPA */}
      <section className="px-4 pb-16">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Horizontal Pod Autoscaler</h2>
          <p className="text-muted-foreground mb-6">
            Automatically scale agents based on CPU and memory utilization.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">hpa.yaml</span>
              <CopyButton text={hpaExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{hpaExample}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Secrets */}
      <section className="px-4 pb-24">
        <div className="container mx-auto max-w-5xl">
          <h2 className="text-2xl font-bold text-foreground mb-4">Secrets Management</h2>
          <p className="text-muted-foreground mb-6">
            Secure credential management with native secrets or External Secrets Operator.
          </p>
          <div className="rounded-xl bg-black border border-border overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border">
              <span className="text-xs text-muted-foreground">secrets.yaml</span>
              <CopyButton text={secretsExample} />
            </div>
            <pre className="p-4 overflow-x-auto text-sm">
              <code className="text-green-400/90 font-mono whitespace-pre">{secretsExample}</code>
            </pre>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
