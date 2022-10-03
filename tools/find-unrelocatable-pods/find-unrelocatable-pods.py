#!/usr/bin/env python3
import openshift

if __name__ == '__main__':

    control_plane_nodes = openshift.selector('nodes', labels={'!node-role.kubernetes.io/master': None}).names()
    print(f'Found control plane nodes: {control_plane_nodes}')

    print('Querying all pods in the cluster -- this may take several minutes...')
    for apiobj in openshift.selector('pods', all_namespaces=True):

        if apiobj.model.status.phase not in ('Pending', 'Running'):
            continue

        if apiobj.model.spec.nodeName in control_plane_nodes:
            # The pod is running on master; no need to relocate
            continue

        owner_kinds = set()
        for reference in apiobj.model.metadata.ownerReferences:
            owner_kinds.add(reference.kind)

        if apiobj.get_annotation('cluster-autoscaler.kubernetes.io/safe-to-evict', if_missing="false") == "true":
            continue

        unrelocatable_reasons = []

        for volume_def in apiobj.model.spec.volumes:
            if volume_def.hostPath or volume_def.emptyDir is not openshift.model.MissingModel:
                unrelocatable_reasons.append('HasLocalStorage')
                break

        relocatable_kinds = set(['ReplicaSet', 'DaemonSet', 'StatefulSet'])
        if len(owner_kinds.intersection(relocatable_kinds)) == 0:
            unrelocatable_reasons.append('NoPodController')

        if unrelocatable_reasons:
            print(f'Pod: {apiobj.fqname()} : may not be relocatable due to: {unrelocatable_reasons}')

