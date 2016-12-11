#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import time, datetime

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class OpenStackHandler(object):
    """
    Operate OpenStack
    """

    def __init__(self, username, password, tenant, url, api):
        self.username = username
        self.password = password
        self.tenant = tenant
        self.url = url
        self.api = api
        self.OpenStack = None
        self.driver = None
        self.init_connection()

    def init_connection(self):
        try:
            self.OpenStack = get_driver(Provider.OPENSTACK)
            self.driver = self.OpenStack(self.username, self.password,
                                         ex_tenant_name=self.tenant,
                                         ex_force_auth_url=self.url,
                                         ex_force_auth_version=self.api)
        except:
            raise Exception("Failed to connect to OpenStack")


class Image(OpenStackHandler):
    """
    Operate Image
    """

    def __init__(self, username, password, tenant, url, api):
        super(Image, self).__init__(username, password, tenant, url, api)

    def images(self):
        """
        List all images
        :return: json images
        """
        try:
            images = self.driver.list_images()
            if images is not None:
                _images = []
                for image in images:
                    create = image.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ").replace("Z", ""),
                            "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'imageId': image.id, 'name': image.name, 'uuid': image.uuid,
                         'status': image.extra.get('status'),
                         'gmtCreate': gmtCreate}
                    _images.append(d)
                return json.dumps(_images)
            else:
                return None
        except:
            raise Exception("Failed to list images")

    def delete_image(self, image_id):
        """
        Delete image
        :param image_id:
        :return: True|False
        """
        try:
            image = self.driver.get_image(image_id)
            if image is not None:
                return self.driver.delete_image(image)
            else:
                return False
        except:
            raise Exception("Failed to delete image")


class Volume(OpenStackHandler):
    """
    Operate Volume
    """

    def __init__(self, username, password, tenant, url, api):
        super(Volume, self).__init__(username, password, tenant, url, api)

    def volumes(self):
        """
        List all volumes from OpenStack
        :return: json volumes
        """
        # try:
        volumes = self.driver.list_volumes()
        if volumes is not None:
            _volumes = []
            for volume in volumes:
                create = volume.extra.get('created_at')
                if create is not None:
                    gmtCreate = str(datetime.strptime(
                        create.replace("T", " ")[: -7], "%Y-%m-%d %H:%M:%S"))
                else:
                    gmtCreate = None
                d = {'volumeId': volume.id, 'name': volume.name, 'size': volume.size, 'status': volume.state,
                     'uuid': volume.uuid,
                     'gmtCreate': gmtCreate}
                _volumes.append(d)
            return json.dumps(_volumes)
        else:
            return None
            # except:
            #     raise Exception("Failed to list volumes")

    def get_volume(self, volume_id):
        """
        Get volume
        :param volume_id:
        :return:
        """
        try:
            volume = self.driver.ex_get_volume(volume_id)
            if volume is not None:
                create = volume.extra.get('created')
                if create is not None:
                    gmtCreate = str(datetime.strptime(
                        create.replace("T", " ")[: -7], "%Y-%m-%d %H:%M:%S"))
                else:
                    gmtCreate = None
                d = {'volumeId': volume.id, 'name': volume.name, 'size': volume.size, 'status': volume.state,
                     'uuid': volume.uuid,
                     'gmtCreate': gmtCreate}
                return json.dumps(d)
            else:
                return None
        except:
            raise Exception("Failed to get volume")

    def create_volume(self, size, name, location='nova', snapshot=None,
                      ex_volume_type=''):
        """
        Create StorageVolume
        :param size:
        :param name:
        :param location:
        :param snapshot:
        :param ex_volume_type:
        :return: json StorageVolume
        """
        try:
            volume = self.driver.create_volume(size, name, location=location, snapshot=snapshot,
                                               ex_volume_type=ex_volume_type)
            if volume is not None:
                create = volume.extra.get('created')
                if create is not None:
                    gmtCreate = str(datetime.strptime(
                        create.replace("T", " ")[: -7], "%Y-%m-%d %H:%M:%S"))
                else:
                    gmtCreate = None
                d = {'volumeId': volume.id, 'name': volume.name, 'size': volume.size, 'status': volume.state,
                     'uuid': volume.uuid,
                     'gmtCreate': gmtCreate}
                return json.dumps(d)
            else:
                return None
        except:
            raise Exception("Failed to create volume")

    def delete_volume(self, volume_id):
        """
        delete volume
        :param volume_id:
        :return: True|False
        """
        try:
            volume = self.driver.ex_get_volume(volume_id)
            if volume is not None:
                return self.driver.destroy_volume(volume)
            else:
                return False
        except:
            raise Exception("Failed to delete volume")


class Snapshot(OpenStackHandler):
    """
    Operate Snapshot
    """

    def __init__(self, username, password, tenant, url, api):
        super(Snapshot, self).__init__(username, password, tenant, url, api)

    def create_volume_snapshot(self, volume_id, name):
        """
        Create volume snapshot
        :param volume_id:
        :param name:
        :return: json volume snapshot
        """
        try:
            volume = self.driver.ex_get_volume(volume_id)
            if volume is not None:
                volume_snapshot = self.driver.ex_create_snapshot(volume, name, description=name)
                if volume_snapshot is not None:
                    create = volume_snapshot.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ")[:-7], "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'snapshotId': volume_snapshot.id, 'size': volume_snapshot.size,
                         'status': volume_snapshot.state,
                         'volumeId': volume_snapshot.extra.get('volume_id'),
                         'gmtCreate': gmtCreate,
                         'remark': volume_snapshot.extra.get('description'),
                         'name': volume_snapshot.extra.get('name')}
                    return json.dumps(d)
                else:
                    return None
            else:
                None
        except:
            raise Exception("Failed to create volume snapshot")

    def snapshots(self):
        """
        List all snapshots
        :return: json snapshots
        """
        try:
            snapshots = self.driver.ex_list_snapshots()
            if snapshots is not None:
                _snapshots = []
                for snapshot in snapshots:
                    create = snapshot.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ")[:-7], "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'snapshotId': snapshot.id, 'size': snapshot.size, 'status': snapshot.state,
                         'volumeId': snapshot.extra.get('volume_id'),
                         'gmtCreate': gmtCreate,
                         'remark': snapshot.extra.get('description'), 'name': snapshot.extra.get('name')}
                    _snapshots.append(d)
                return json.dumps(_snapshots)
            else:
                return None
        except:
            raise Exception("Failed to list snapshots")

    def get_snapshot(self, snapshot_id):
        """
        Get snapshot
        :param snapshot_id:
        :return:
        """
        try:
            snapshots = self.driver.ex_list_snapshots()
            if snapshots is not None:
                for snapshot in snapshots:
                    if snapshot.id == snapshot_id:
                        create = snapshot.extra.get('created')
                        if create is not None:
                            gmtCreate = str(datetime.strptime(
                                create.replace("T", " ")[:-7], "%Y-%m-%d %H:%M:%S"))
                        else:
                            gmtCreate = None
                        d = {'snapshotId': snapshot.id, 'size': snapshot.size, 'status': snapshot.state,
                             'volumeId': snapshot.extra.get('volume_id'),
                             'gmtCreate': gmtCreate,
                             'remark': snapshot.extra.get('description'), 'name': snapshot.extra.get('name')}
                        return json.dumps(d)
                    else:
                        return None
            else:
                return None
        except:
            raise Exception("Failed to delete snapshot")

    def volume_snapshots(self, volume_id):
        """
        List all volume snapshots
        :param volume_id:
        :return: json volume snapshots
        """
        try:
            volume = self.driver.ex_get_volume(volume_id)
            if volume is not None:
                volume_snapshots = self.driver.list_volume_snapshots(volume)
                _volume_snapshots = []
                for volume_snapshot in volume_snapshots:
                    volume_id = volume_snapshot.extra.get('volume_id')
                    volume_name = None
                    if volume_id is not None:
                        volume = self.driver.ex_get_volume(volume_id)
                        if volume is not None:
                            volume_name = volume.name
                    create = volume_snapshot.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ")[:-7], "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'snapshotId': volume_snapshot.id, 'size': volume_snapshot.size,
                         'status': volume_snapshot.state,
                         'volumeId': volume_snapshot.extra.get('volume_id'), 'volumeName': volume_name,
                         'gmtCreate': gmtCreate,
                         'remark': volume_snapshot.extra.get('description'),
                         'name': volume_snapshot.extra.get('name')}
                    _volume_snapshots.append(d)
                return json.dumps(_volume_snapshots)
            else:
                return None
        except:
            raise Exception("Failed to list volume snapshots")

    def delete_snapshot(self, snapshot_id):
        """
        Delete snapshot
        :param snapshot:
        :return:
        """
        try:
            snapshots = self.driver.ex_list_snapshots()
            if snapshots is not None:
                for snapshot in snapshots:
                    if snapshot.id == snapshot_id:
                        return self.driver.ex_delete_snapshot(snapshot)
                    else:
                        continue
            else:
                return False
        except:
            raise Exception("Failed to delete snapshot")


class Size(OpenStackHandler):
    """
    Operate Size
    """

    def __init__(self, username, password, tenant, url, api):
        super(Size, self).__init__(username, password, tenant, url, api)

    def sizes(self):
        """
        List sizes
        :return: json sizes
        """
        try:
            sizes = self.driver.list_sizes()
            if sizes is not None:
                _sizes = []
                for size in sizes:
                    d = {'flavorId': size.id, 'name': size.name, 'memory': size.ram,
                         'uuid': size.uuid, 'cpu': size.vcpus, 'disk': size.disk}
                    _sizes.append(d)
                return json.dumps(_sizes)
            else:
                return None
        except:
            raise Exception("Failed to list sizes")


class Node(OpenStackHandler):
    """
    Operate Node
    """

    def __init__(self, username, password, tenant, url, api):
        super(Node, self).__init__(username, password, tenant, url, api)

    def nodes(self):
        """
        List nodes
        :return:
        """
        try:
            nodes = self.driver.list_nodes()
            if nodes is not None:
                _nodes = []
                for node in nodes:
                    create = node.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'instanceId': node.id, 'name': node.name, 'imageId': node.extra.get('imageId'),
                         'flavorId': node.extra.get("flavorId"), 'status': node.extra.get("vm_state"),
                         'uuid': node.uuid, 'privateIps': node.private_ips, 'publicIps': node.public_ips,
                         'gmtCreate': gmtCreate}
                    _nodes.append(d)
                return json.dumps(_nodes)
            else:
                return None
        except:
            raise Exception("Failed to get nodes")

    def get_node(self, node_id):
        """
        Get node
        :param node_id:
        :return:
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                create = node.extra.get('created')
                if create is not None:
                    gmtCreate = str(datetime.strptime(
                        create.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"))
                else:
                    gmtCreate = None
                d = {'instanceId': node.id, 'name': node.name, 'imageId': node.extra.get('imageId'),
                     'flavorId': node.extra.get("flavorId"), 'status': node.extra.get("vm_state"),
                     'uuid': node.uuid, 'privateIps': node.private_ips, 'publicIps': node.public_ips,
                     'gmtCreate': gmtCreate}
                return json.dumps(d)
            else:
                return None
        except:
            raise Exception("Failed to get node")

    def create_node(self, name, image_id, size_id, network_id):
        """
        Create node
        :param name:
        :param image_id:
        :param size_id:
        :return: json node
        """
        try:
            image = self.driver.get_image(image_id)
            size = self.driver.ex_get_size(size_id)
            networks = self.driver.ex_list_networks()
            net = None
            for network in networks:
                if network.id == network_id:
                    net = network
            if image is not None and size is not None and networks is not None:
                node = self.driver.create_node(name=name, image=image, size=size, networks=[net])
                if node is not None:
                    create = node.extra.get('created')
                    if create is not None:
                        gmtCreate = str(datetime.strptime(
                            create.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S"))
                    else:
                        gmtCreate = None
                    d = {'instanceId': node.id, 'name': node.name, 'imageId': node.extra.get('imageId'),
                         'flavorId': node.extra.get("flavorId"), 'status': node.extra.get("vm_state"),
                         'uuid': node.uuid, 'privateIps': node.private_ips, 'publicIps': node.public_ips,
                         'gmtCreate': gmtCreate}
                    return json.dumps(d)
                else:
                    return None
            else:
                return None
        except:
            raise Exception("Failed to create node")

    def reboot_node(self, node_id):
        """
        reboot node
        :param node_id:
        :return:
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.ex_hard_reboot_node(node)
            else:
                return False
        except:
            raise Exception("Failed to reboot node")

    def update_node(self, node_id, name):
        """
        Update node
        :param node_id:
        :param name:
        :return: json node
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                _node = self.driver.ex_update_node(node, name=name)
                if _node is not None:
                    d = {'instanceId': _node.id, 'name': _node.name, 'imageId': _node.image, 'size': _node.size,
                         'status': _node.state, 'uuid': _node.uuid, 'privateIps': _node.private_ips,
                         'publicIps': _node.public_ips}
                    return json.dumps(d)
            else:
                return None
        except:
            raise Exception("Failed to update node")

    def delete_node(self, node_id):
        """
        Delete node
        :param node_id:
        :return: True|False
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.destroy_node(node)
            else:
                return False
        except:
            raise Exception("Failed to delete node")

    def pause_node(self, node_id):
        """
        Stop node
        :param node_id:
        :return: True|False
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.ex_pause_node(node)
            else:
                return False
        except:
            raise Exception("Failed to stop node")

    def unpause_node(self, node_id):
        """
        Start node
        :param node_id:
        :return: True|False
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.ex_unpause_node(node)
            else:
                return False
        except:
            raise Exception("Failed to start node")

    def suspend_node(self, node_id):
        """
        Suspend node
        :param node_id:
        :return:
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.ex_suspend_node(node)
            else:
                return False
        except:
            raise Exception("Failed to suspend node")

    def active_node(self, node_id):
        """
        Active node
        :param node_id:
        :return:
        """
        try:
            node = self.driver.ex_get_node_details(node_id)
            if node is not None:
                return self.driver.ex_resume_node(node)
            else:
                return False
        except:
            raise Exception("Failed to active node")


class Network(OpenStackHandler):
    """
    Operate Network
    """

    def __init__(self, username, password, tenant, url, api):
        super(Network, self).__init__(username, password, tenant, url, api)

    def networks(self):
        """
        List networks
        :return:
        """
        try:
            networks = self.driver.ex_list_networks()
            if networks is not None:
                _networks = []
                for network in networks:
                    d = {'networkId': network.id, 'name': network.name, 'cidr': network.cidr}
                    _networks.append(d)
                return json.dumps(_networks)
            else:
                return None

        except:
            raise Exception("Failed to list networks")

    def create_network(self, name, cidr):
        """
        Create network
        :param name:
        :param cidr:
        :return:
        """
        try:
            network = self.driver.ex_create_network(name, cidr)
            if network is not None:
                d = {'networkId': network.id, 'name': network.name, 'cidr': network.cidr}
                return json.dumps(d)
            else:
                return None
        except:
            raise Exception("Failed to create network")

    def delete_network(self, network_id):
        """
        Delete network
        :param network_id:
        :return:
        """
        try:
            networks = self.driver.ex_list_networks()
            for network in networks:
                if network.id == network_id:
                    return self.driver.ex_delete_network(network)
                else:
                    continue
            else:
                return False
        except:
            raise Exception("Failed to delete network")


if __name__ == '__main__':
    _username = 'admin'
    _password = 'Root1234'
    _url = 'http://192.168.1.211:35357'
    _tenant = 'admin'
    _api = '2.0_password'
    node = Node(_username, _password, _tenant, _url, _api)
    print node.get_node('fb5253b3-29cd-40a0-aff2-d89a584e73e5')
