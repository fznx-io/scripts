from google.cloud import compute_v1
from google.oauth2 import service_account
from secrets import GCP_PROJECT_ID, GCP_REGION, GCP_ZONE

def reserve_static_ip(project_id, region, address_name):
    address_client = compute_v1.AddressesClient()

    address = compute_v1.Address(name=address_name)
    operation = address_client.insert(project=project_id, region=region, address_resource=address)

    # Wait for the operation to complete
    operation_client = compute_v1.RegionOperationsClient()
    result = operation_client.wait(project=project_id, region=region, operation=operation.name)

    if result.error:
        raise Exception(f"Failed to reserve static IP: {result.error}")
    else:
        # Retrieve the reserved IP address
        response = address_client.get(project=project_id, region=region, address=address_name)
        print(f"Reserved static IP: {response.address}")
        return response.address

def create_vm(project_id, zone, instance_name, machine_type, source_image, startup_script, external_ip):
    # Initialize the client
    instance_client = compute_v1.InstancesClient()

    # Define the machine type (e.g., "n1-standard-1")
    machine_type_path = f"zones/{zone}/machineTypes/{machine_type}"

    # Define the image to use
    image_client = compute_v1.ImagesClient()
    image_response = image_client.get_from_family(project="debian-cloud", family=source_image)
    source_disk_image = image_response.self_link

    # Define the startup script metadata
    metadata_items = [
        {
            "key": "startup-script",
            "value": startup_script,
        }
    ]

    # Define the disk
    disk = compute_v1.AttachedDisk()
    initialize_params = compute_v1.AttachedDiskInitializeParams(
        source_image=source_disk_image,
        disk_size_gb=10,  # Specify disk size (in GB)
        disk_type=f"zones/{zone}/diskTypes/pd-standard",
    )
    disk.auto_delete = True
    disk.boot = True
    disk.initialize_params = initialize_params

    # Define the network interface with an external static IP
    network_interface = compute_v1.NetworkInterface(
        name="global/networks/default",
        access_configs=[compute_v1.AccessConfig(name="External NAT", nat_ip=external_ip)],
    )

    # Create the instance configuration
    instance = compute_v1.Instance(
        name=instance_name,
        machine_type=machine_type_path,
        disks=[disk],
        network_interfaces=[network_interface],
        metadata=compute_v1.Metadata(items=metadata_items),
    )

    # Create the instance in the specified project and zone
    operation = instance_client.insert(project=project_id, zone=zone, instance_resource=instance)

    print(f"Creating instance {instance_name}...")

    # Wait for the operation to complete
    operation_client = compute_v1.ZoneOperationsClient()
    result = operation_client.wait(project=project_id, zone=zone, operation=operation.name)

    if result.error:
        print(f"Failed to create instance {instance_name}: {result.error}")
    else:
        print(f"Instance {instance_name} created successfully.")

if __name__ == "__main__":
    # Define GCP project details
    PROJECT_ID = GCP_PROJECT_ID
    REGION = GCP_REGION
    ZONE = GCP_ZONE
    INSTANCE_NAME = "atlantis-vm"
    MACHINE_TYPE = "e2-medium"
    SOURCE_IMAGE_FAMILY = "debian-10"  # Debian family image
    STATIC_IP_NAME = "atlantis-static-ip"  # Name for the reserved IP

    # Reserve a static external IP
    reserved_ip = reserve_static_ip(PROJECT_ID, REGION, STATIC_IP_NAME)

    # Define the startup script to install Atlantis, using the reserved static IP
    STARTUP_SCRIPT = f"""#!/bin/bash
    # Update and install dependencies
    apt-get update
    apt-get install -y wget unzip curl

    # Download and install Atlantis
    wget https://github.com/runatlantis/atlantis/releases/download/v0.17.3/atlantis_linux_amd64.zip
    unzip atlantis_linux_amd64.zip
    mv atlantis /usr/local/bin/

    # Create a directory for Atlantis data
    mkdir -p /etc/atlantis

    # Set up a basic config file (you should customize this as needed)
    cat <<EOF > /etc/atlantis/config.yaml
    atlantis-url: http://{reserved_ip}:4141
    EOF

    # Start Atlantis on boot
    echo "[Unit]
    Description=Atlantis

    [Service]
    ExecStart=/usr/local/bin/atlantis server --config /etc/atlantis/config.yaml

    [Install]
    WantedBy=multi-user.target" > /etc/systemd/system/atlantis.service

    # Enable and start the Atlantis service
    systemctl enable atlantis.service
    systemctl start atlantis.service
    """

    # Create the VM
    create_vm(PROJECT_ID, ZONE, INSTANCE_NAME, MACHINE_TYPE, SOURCE_IMAGE_FAMILY, STARTUP_SCRIPT, reserved_ip)
