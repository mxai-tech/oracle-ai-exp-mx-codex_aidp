# Autenticación proporcionada por OCI Resource Manager; no enviar PEM ni API key.
provider "oci" {
  region = var.region
}

# Las escrituras de IAM deben usar la región principal de la tenancy, que puede ser distinta de la región de AIDP.
data "oci_identity_region_subscriptions" "tenancy" {
  tenancy_id = var.tenancy_ocid
}

locals {
  home_region = one([
    for r in data.oci_identity_region_subscriptions.tenancy.region_subscriptions :
    r.region_name if r.is_home_region
  ])
}

provider "oci" {
  alias  = "home"
  region = local.home_region
}
