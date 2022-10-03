# Find Unrelocatable Pods
Requires: https://pypi.org/project/openshift-client/

The OpenShift autoscaler will attempt to scale down a cluster when it over-provisioned relative to the requirements of running pod resource requests.

It will do so by draining nodes which pods which can successfully be recreated on existing nodes. However, it will avoid draining nodes which have pods that:
1. Are using local storage.
2. Are not managed by a DaemonSet, ReplicaSet, or other controller which will reschedule the pod's workload when drained.
* There are other reasons, like PDBs, but it is assumed the user is aware of these explicit drain inhibitors.

In other words, the autoscaler will allow a cluster to remain overprovisioned in order to not disrupt pods which may not be able to resume work successfully on another node.

This tool finds pods which fit these criteria and which may be preventing the autoscaler from working effectively to right-size your cluster. 

The easiest way to enable these pods to be rescheduled by the autoscaler is to annotate them with `cluster-autoscaler.kubernetes.io/safe-to-evict: "true"`. This permits the autoscaler to ignore its default safeguards.

