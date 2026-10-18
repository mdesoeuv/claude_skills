---
name: kubernetes
description: Write, review and operate Kubernetes workloads on EKS — manifests, Helm charts, Kustomize, resource requests/limits, probes, security contexts, IRSA/Pod Identity, and safe kubectl usage. Use for any YAML with apiVersion/kind, Helm values, "deploy this to the cluster", "pod is crashlooping", HPA, ingress, or kubectl commands.
metadata:
  tier: recommended
---

# Kubernetes on EKS

A Deployment without requests, probes, and a security context will run fine until the day it takes a node down with it.

## Before kubectl does anything

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{.contexts[0].context.namespace}'
```

Say which cluster and namespace you are in. Always pass `-n <ns>` and, for mutating commands against prod, `--context` explicitly. Prefer `kubectl diff -f` and `kubectl apply --dry-run=server -f` before `apply`. Never `kubectl delete` namespaces, PVCs, or CRDs without explicit confirmation.

Changes to things managed by Argo CD/Flux/Helm belong in git, not in `kubectl edit`.

## Workload checklist

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 2
  strategy: { type: RollingUpdate, rollingUpdate: { maxUnavailable: 0, maxSurge: 1 } }
  template:
    spec:
      serviceAccountName: api           # IRSA / Pod Identity, never node role
      securityContext:
        runAsNonRoot: true
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: api
          image: 123456789012.dkr.ecr.eu-west-1.amazonaws.com/api@sha256:<digest>
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits: { memory: 512Mi }        # CPU limit optional; memory limit mandatory
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: [ALL] }
          readinessProbe: { httpGet: { path: /healthz, port: 8080 }, periodSeconds: 5 }
          livenessProbe:  { httpGet: { path: /livez,   port: 8080 }, periodSeconds: 10, failureThreshold: 3 }
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: api } }
```

Pair with a `PodDisruptionBudget` (`minAvailable: 1`), an `HPA` on CPU or a custom metric, and `NetworkPolicy` default-deny in the namespace.

## Rules

- Images by digest or immutable tag; `imagePullPolicy: IfNotPresent` is fine when tags are immutable.
- Requests reflect real usage (look at `kubectl top` or metrics); limits on memory prevent OOM taking neighbours.
- Readiness and liveness are different endpoints. Liveness must not depend on downstreams, or a DB blip restarts the fleet.
- Secrets come from External Secrets Operator or Secrets Store CSI backed by Secrets Manager; no `kind: Secret` with data in git.
- AWS access through IRSA or EKS Pod Identity with a scoped role (see `iam-least-privilege`); never the node instance role.
- Namespaces per team or service with ResourceQuota and LimitRange.
- Helm: `helm template` and `helm diff upgrade` before `helm upgrade --install --atomic --timeout 5m`. Values files per env; no secrets in values.

## Debugging

```bash
kubectl get pods -n ns -o wide
kubectl describe pod <pod> -n ns          # events at the bottom
kubectl logs <pod> -n ns --previous       # last crashed container
kubectl get events -n ns --sort-by=.lastTimestamp | tail -30
kubectl exec -it <pod> -n ns -- sh        # only if the image has a shell
```

`CrashLoopBackOff`: logs of the previous container. `ImagePullBackOff`: ECR auth, image name, node role. `Pending`: `describe` events show insufficient resources, taints, PVC binding, or zone affinity. `OOMKilled`: raise memory limit or fix the leak; check `lastState.terminated.reason`.
