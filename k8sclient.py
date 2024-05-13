import logging
import sys
from kubernetes import client, config
from kubernetes.client import ApiException

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()


class K8SClient(object):
    def __init__(self):
        try:
            # config.load_incluster_config()
            config.load_kube_config()
            logger.info("Successfully loaded kubeconfig file.")
        except Exception as e:
            logger.error(e)

        self.v1 = client.CoreV1Api()

    def get_all_pods(self) -> dict:
        try:
            list_pod_for_all_namespaces = self.v1.list_pod_for_all_namespaces(watch=False, timeout_seconds=30)
        except ApiException as e:
            logger.error(e)
            return {"CODE": e.status, "BODY": e.body, "REASON": e.reason}

        list_pods = []
        for pod in list_pod_for_all_namespaces.items:
            if pod.status.container_statuses is not None and len(pod.status.container_statuses) > 0:
                if pod.status.container_statuses[0].restart_count is not None:
                    restart_count = int(pod.status.container_statuses[0].restart_count)
                else:
                    restart_count = 0
            else:
                restart_count = 0

            containers = []
            for container in pod.spec.containers:
                envs = {}
                if container.env:
                    for env in container.env:
                        envs.update({str(env.name): str(env.value) if env.value else "Value not set or using secret/configMap"})
                else:
                    envs = None
                containers.append({'image': container.image, 'envs': envs})

            list_pods.append({'NAMESPACE': pod.metadata.namespace,
                              'POD_NAME': pod.metadata.name,
                              'STATUS': pod.status.phase,
                              'RESTARTS': restart_count,
                              'CONTAINERS': containers})
        logger.info(f"v1.list_pod_for_all_namespaces: {len(list_pods)} pods returned")

        return {"CODE": 200, "BODY": list_pods, "REASON": None}


if __name__ == "__main__":
    cluster = K8SClient()
    cluster.get_all_pods()
