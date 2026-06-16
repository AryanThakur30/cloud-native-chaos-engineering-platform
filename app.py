
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from kubernetes import client, config
from prometheus_client import Counter, generate_latest
from database import conn, cursor

app = FastAPI(
    title="Cloud Native Chaos Engineering Platform",
    description="Chaos Engineering APIs for Kubernetes",
    version="3.0"
)

# --------------------------------------------------
# PROMETHEUS METRICS
# --------------------------------------------------

TOTAL_EXPERIMENTS = Counter(
    "chaos_experiments_total",
    "Total chaos experiments executed"
)

POD_KILL_COUNTER = Counter(
    "pod_kill_total",
    "Total pod kill experiments"
)

CPU_STRESS_COUNTER = Counter(
    "cpu_stress_total",
    "Total cpu stress experiments"
)

MEMORY_STRESS_COUNTER = Counter(
    "memory_stress_total",
    "Total memory stress experiments"
)

NETWORK_CHAOS_COUNTER = Counter(
    "network_chaos_total",
    "Total network chaos experiments"
)

# --------------------------------------------------
# KUBERNETES CONFIG
# --------------------------------------------------

try:
    config.load_incluster_config()
    print("Running inside Kubernetes cluster")

except:

    try:
        config.load_kube_config()
        print("Loaded local kubeconfig")

    except:

        print("Kubernetes config not found.")
        print("Running in standalone mode.")

# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "project": "Cloud Native Chaos Engineering Platform",
        "status": "healthy",
        "version": "3.0"
    }

# --------------------------------------------------
# POD KILL
# --------------------------------------------------

@app.post("/experiments/pod-kill")
def pod_kill(namespace: str, pod_name: str):

    try:

        v1 = client.CoreV1Api()

        v1.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace
        )

        cursor.execute(
            """
            INSERT INTO experiments
            (experiment, namespace, target, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                "pod-kill",
                namespace,
                pod_name,
                "success"
            )
        )

        conn.commit()

        TOTAL_EXPERIMENTS.inc()
        POD_KILL_COUNTER.inc()

        return {
            "status": "success",
            "experiment": "pod-kill",
            "target": pod_name
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# CPU STRESS
# --------------------------------------------------

@app.post("/experiments/cpu-stress")
def cpu_stress(namespace: str):

    try:

        v1 = client.CoreV1Api()

        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "cpu-stress-test"
            },
            "spec": {
                "restartPolicy": "Never",
                "containers": [
                    {
                        "name": "stress",
                        "image": "alpine",
                        "command": [
                            "sh",
                            "-c",
                            "while true; do yes > /dev/null; done"
                        ]
                    }
                ]
            }
        }

        v1.create_namespaced_pod(
            namespace=namespace,
            body=pod_manifest
        )

        cursor.execute(
            """
            INSERT INTO experiments
            (experiment, namespace, target, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                "cpu-stress",
                namespace,
                "-",
                "success"
            )
        )

        conn.commit()

        TOTAL_EXPERIMENTS.inc()
        CPU_STRESS_COUNTER.inc()

        return {
            "status": "success",
            "experiment": "cpu-stress"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# MEMORY STRESS
# --------------------------------------------------

@app.post("/experiments/memory-stress")
def memory_stress(namespace: str):

    try:

        v1 = client.CoreV1Api()

        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "memory-stress-test"
            },
            "spec": {
                "restartPolicy": "Never",
                "containers": [
                    {
                        "name": "memory-stress",
                        "image": "alpine",
                        "command": [
                            "sh",
                            "-c",
                            "tail /dev/zero | head -c 500M > /dev/null && sleep 300"
                        ]
                    }
                ]
            }
        }

        v1.create_namespaced_pod(
            namespace=namespace,
            body=pod_manifest
        )

        cursor.execute(
            """
            INSERT INTO experiments
            (experiment, namespace, target, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                "memory-stress",
                namespace,
                "-",
                "success"
            )
        )

        conn.commit()

        TOTAL_EXPERIMENTS.inc()
        MEMORY_STRESS_COUNTER.inc()

        return {
            "status": "success",
            "experiment": "memory-stress"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# NETWORK CHAOS
# --------------------------------------------------

@app.post("/experiments/network-chaos")
def network_chaos(namespace: str):

    cursor.execute(
        """
        INSERT INTO experiments
        (experiment, namespace, target, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            "network-chaos",
            namespace,
            "-",
            "success"
        )
    )

    conn.commit()

    TOTAL_EXPERIMENTS.inc()
    NETWORK_CHAOS_COUNTER.inc()

    return {
        "status": "success",
        "experiment": "network-chaos"
    }

# --------------------------------------------------
# POD LIST
# --------------------------------------------------

@app.get("/pods")
def list_pods(namespace: str = "default"):

    try:

        v1 = client.CoreV1Api()

        pods = v1.list_namespaced_pod(namespace)

        return {
            "namespace": namespace,
            "pods": [
                pod.metadata.name
                for pod in pods.items
            ]
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# HISTORY
# --------------------------------------------------

@app.get("/history")
def history():

    cursor.execute(
        """
        SELECT
        id,
        experiment,
        namespace,
        target,
        status
        FROM experiments
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    history_data = []

    for row in rows:

        history_data.append(
            {
                "id": row[0],
                "experiment": row[1],
                "namespace": row[2],
                "target": row[3],
                "status": row[4]
            }
        )

    return {
        "total_experiments": len(history_data),
        "experiments": history_data
    }

# --------------------------------------------------
# CLUSTER HEALTH
# --------------------------------------------------

@app.get("/cluster-health")
def cluster_health():

    try:

        v1 = client.CoreV1Api()

        pods = v1.list_pod_for_all_namespaces()

        running = 0
        failed = 0

        for pod in pods.items:

            if pod.status.phase == "Running":
                running += 1

            if pod.status.phase == "Failed":
                failed += 1

        return {
            "cluster_status": "healthy",
            "total_pods": len(pods.items),
            "running_pods": running,
            "failed_pods": failed
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# METRICS
# --------------------------------------------------

@app.get("/metrics")
def metrics():

    return PlainTextResponse(
        generate_latest().decode("utf-8")
    )
