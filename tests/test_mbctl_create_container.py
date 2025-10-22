import unittest

from mbctl.exec.create_nspawn_container_from_oci_url import pull_oci_image_and_create_container

mirror_list = [
    "gcr.nju.edu.cn/google-containers/alpine-with-bash@sha256:0955672451201896cf9e2e5ce30bec0c7f10757af33bf78b7a6afa5672c596f5"

]

def test_pull_oci_image_and_create_container():
    # pull_oci_image_and_create_container(
    #     oci_image_url="gcr.nju.edu.cn/google-containers/alpine-with-bash@sha256:0955672451201896cf9e2e5ce30bec0c7f10757af33bf78b7a6afa5672c596f5",
    #     container_name="TestContainer",
    #     container_template="network_isolated",
    # )

    pull_oci_image_and_create_container(
        oci_image_url="ghcr.nju.edu.cn/bitwarden/self-host:latest",
        container_name="TestBWContainer",
        container_template="network_isolated",
    )