from fastapi import FastAPI
from kubernetes import client, config

app = FastAPI(
    title="Kubernetes Chaos Engineering Platform",
    description="Chaos Engineering APIs for Kubernetes",
    version="1.0"
)

# Load Kubernetes configuration
config.load_kube_config()


@app.get("/")
def home():
    return {
        "message": "K8s Chaos Platform Running",
        "status": "healthy"
    }


# --------------------------------------------------
# POD KILL EXPERIMENT
# --------------------------------------------------

@app.post("/experiments/pod-kill")
def pod_kill(namespace: str, pod_name: str):

    v1 = client.CoreV1Api()

    try:
        v1.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace
        )

        return {
            "status": "success",
            "experiment": "pod-kill",
            "deleted_pod": pod_name
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# --------------------------------------------------
# CPU STRESS EXPERIMENT
# --------------------------------------------------

@app.post("/experiments/cpu-stress")
def cpu_stress(namespace: str):

    v1 = client.CoreV1Api()

    stress_pod = {
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

    try:
        v1.create_namespaced_pod(
            namespace=namespace,
            body=stress_pod
        )

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
# MEMORY STRESS EXPERIMENT
# --------------------------------------------------

@app.post("/experiments/memory-stress")
def memory_stress(namespace: str):

    v1 = client.CoreV1Api()

    memory_pod = {
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

    try:
        v1.create_namespaced_pod(
            namespace=namespace,
            body=memory_pod
        )

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
# LIST RUNNING PODS
# --------------------------------------------------

@app.get("/pods")
def list_pods(namespace: str = "default"):

    v1 = client.CoreV1Api()

    try:
        pods = v1.list_namespaced_pod(namespace)

        return {
            "namespace": namespace,
            "pods": [pod.metadata.name for pod in pods.items]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }