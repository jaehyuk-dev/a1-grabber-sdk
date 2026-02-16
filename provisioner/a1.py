import oci

from core import config
from core.log import logger
from core.notify import send_slack


def get_oci_config():
    """OCI SDK 인증 설정"""
    return {
        "user": config.USER_OCID,
        "fingerprint": config.FINGERPRINT,
        "tenancy": config.TENANCY_OCID,
        "region": config.REGION,
        "key_file": config.KEY_FILE,
    }


def get_availability_domain(identity_client):
    """가용성 도메인 조회"""
    ads = identity_client.list_availability_domains(config.TENANCY_OCID).data
    return ads[0].name


def get_subnet_id(network_client):
    """퍼블릭 서브넷 ID 조회"""
    subnets = network_client.list_subnets(
        compartment_id=config.COMPARTMENT_OCID,
        display_name=config.SUBNET_DISPLAY_NAME,
    ).data
    if not subnets:
        raise Exception(
            f"퍼블릭 서브넷 '{config.SUBNET_DISPLAY_NAME}'을(를) 찾을 수 없습니다"
        )
    return subnets[0].id


def get_image_id(compute_client):
    """지정된 OS·Shape에 맞는 최신 이미지 ID 조회"""
    images = compute_client.list_images(
        compartment_id=config.COMPARTMENT_OCID,
        operating_system=config.IMAGE_OS,
        operating_system_version=config.IMAGE_OS_VERSION,
        shape=config.SHAPE,
        sort_by="TIMECREATED",
        sort_order="DESC",
    ).data
    if not images:
        raise Exception(
            f"{config.IMAGE_OS} {config.IMAGE_OS_VERSION} ({config.SHAPE}) 이미지를 찾을 수 없습니다"
        )
    return images[0].id


def check_existing_instance(compute_client):
    """이미 A1 인스턴스가 있는지 확인 (RUNNING/PROVISIONING/STARTING)"""
    for state in ("RUNNING", "PROVISIONING", "STARTING"):
        instances = compute_client.list_instances(
            compartment_id=config.COMPARTMENT_OCID,
            display_name=config.DISPLAY_NAME,
            lifecycle_state=state,
        ).data
        if instances:
            return True
    return False


def create_a1_instance():
    """A1 인스턴스 생성 시도"""
    oci_config = get_oci_config()
    oci.config.validate_config(oci_config)

    identity_client = oci.identity.IdentityClient(oci_config)
    compute_client = oci.core.ComputeClient(oci_config)
    network_client = oci.core.VirtualNetworkClient(oci_config)

    # 이미 있으면 스킵
    if check_existing_instance(compute_client):
        logger.info("이미 A1 인스턴스가 실행 중 — 스킵")
        return False

    # 필요한 정보 수집
    ad_name = get_availability_domain(identity_client)
    subnet_id = get_subnet_id(network_client)
    image_id = get_image_id(compute_client)

    # 인스턴스 생성 요청
    launch_details = oci.core.models.LaunchInstanceDetails(
        availability_domain=ad_name,
        compartment_id=config.COMPARTMENT_OCID,
        display_name=config.DISPLAY_NAME,
        shape=config.SHAPE,
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=config.OCPUS,
            memory_in_gbs=config.MEMORY_IN_GBS,
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            source_type="image",
            image_id=image_id,
            boot_volume_size_in_gbs=config.BOOT_VOLUME_SIZE_IN_GBS,
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=subnet_id,
            assign_public_ip=True,
        ),
        metadata={"ssh_authorized_keys": config.SSH_PUBLIC_KEY},
    )

    response = compute_client.launch_instance(launch_details)
    instance = response.data

    logger.info(f"A1 인스턴스 생성 성공! ID: {instance.id}")
    logger.info(f"상태: {instance.lifecycle_state}")

    send_slack(
        f":tada: *A1 인스턴스 확보 성공!*\n• ID: `{instance.id}`\n• Region: `{config.REGION}`"
    )
    return True
