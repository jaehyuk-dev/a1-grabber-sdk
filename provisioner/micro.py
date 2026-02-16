import oci

from core import config
from core.log import logger
from core.notify import send_slack
from provisioner.a1 import get_availability_domain, get_oci_config, get_subnet_id


def get_micro_image_id(compute_client):
    """Micro Shape에 맞는 최신 이미지 ID 조회"""
    images = compute_client.list_images(
        compartment_id=config.COMPARTMENT_OCID,
        operating_system=config.IMAGE_OS,
        operating_system_version=config.IMAGE_OS_VERSION,
        shape=config.MICRO_SHAPE,
        sort_by="TIMECREATED",
        sort_order="DESC",
    ).data
    if not images:
        raise Exception(
            f"{config.IMAGE_OS} {config.IMAGE_OS_VERSION} ({config.MICRO_SHAPE}) 이미지를 찾을 수 없습니다"
        )
    return images[0].id


def check_existing_micro(compute_client):
    """이미 Micro 인스턴스가 있는지 확인"""
    instances = compute_client.list_instances(
        compartment_id=config.COMPARTMENT_OCID,
        display_name=config.MICRO_DISPLAY_NAME,
        lifecycle_state="RUNNING",
    ).data
    return len(instances) > 0


def create_micro_instance():
    """Micro 인스턴스 생성 시도"""
    oci_config = get_oci_config()
    oci.config.validate_config(oci_config)

    identity_client = oci.identity.IdentityClient(oci_config)
    compute_client = oci.core.ComputeClient(oci_config)
    network_client = oci.core.VirtualNetworkClient(oci_config)

    ad_name = get_availability_domain(identity_client)
    subnet_id = get_subnet_id(network_client)
    image_id = get_micro_image_id(compute_client)

    launch_details = oci.core.models.LaunchInstanceDetails(
        availability_domain=ad_name,
        compartment_id=config.COMPARTMENT_OCID,
        display_name=config.MICRO_DISPLAY_NAME,
        shape=config.MICRO_SHAPE,
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            source_type="image",
            image_id=image_id,
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=subnet_id,
            assign_public_ip=True,
        ),
        metadata={"ssh_authorized_keys": config.SSH_PUBLIC_KEY},
    )

    response = compute_client.launch_instance(launch_details)
    instance = response.data

    logger.info(f"Micro 인스턴스 생성 성공! ID: {instance.id}")
    logger.info(f"상태: {instance.lifecycle_state}")

    send_slack(
        f":tada: *Micro 인스턴스 확보 성공!*\n• ID: `{instance.id}`\n• Region: `{config.REGION}`"
    )
