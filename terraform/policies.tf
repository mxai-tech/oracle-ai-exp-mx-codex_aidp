# No crea usuarios, grupos ni credenciales. El operador usa la sesión autenticada de Resource Manager en su cuenta de prueba.
# Estas autorizaciones pertenecen al SERVICIO AIDP; no otorgan permisos administrativos a participantes.
resource "oci_identity_policy" "service_iam" {
  provider       = oci.home
  compartment_id = var.tenancy_ocid
  name           = "${var.lab_name}-service-iam"
  description    = "Inspección de IAM y uso de etiquetas requeridos por el servicio AIDP."
  freeform_tags  = local.tags
  statements = [
    "Allow any-user to {AUTHENTICATION_INSPECT, DOMAIN_INSPECT, DOMAIN_READ, DYNAMIC_GROUP_INSPECT, GROUP_INSPECT, GROUP_MEMBERSHIP_INSPECT, USER_INSPECT, USER_READ} in tenancy where all {request.principal.type='aidataplatform'}",
    "Allow any-user to {TAG_NAMESPACE_USE} in tenancy where all {request.principal.type='aidataplatform'}",
  ]
  depends_on = [oci_identity_compartment.lab]
}

resource "oci_identity_policy" "service_compartment" {
  provider       = oci.home
  compartment_id = oci_identity_compartment.lab.id
  name           = "${var.lab_name}-service-data"
  description    = "Acceso del servicio AIDP a datos, registros y métricas solo en el compartment del laboratorio."
  freeform_tags  = local.tags
  statements = concat([
    "Allow any-user to manage log-groups in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform'}",
    "Allow any-user to read log-content in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform'}",
    "Allow any-user to use metrics in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform', target.metrics.namespace='oracle_aidataplatform'}",
    "Allow any-user to manage buckets in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform', any {request.permission='BUCKET_CREATE', request.permission='BUCKET_INSPECT', request.permission='BUCKET_READ', request.permission='BUCKET_UPDATE'}}",
    "Allow any-user to manage buckets in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.id=target.resource.tag.orcl-aidp.governingAidpId, any {request.permission='BUCKET_DELETE', request.permission='PAR_MANAGE', request.permission='RETENTION_RULE_LOCK', request.permission='RETENTION_RULE_MANAGE'}}",
    "Allow any-user to read objectstorage-namespaces in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform', request.permission='OBJECTSTORAGE_NAMESPACE_READ'}",
    "Allow any-user to manage objects in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.id=target.bucket.system-tag.orcl-aidp.governingAidpId}",
    ], var.enable_ai_features ? [
    "Allow any-user to use generative-ai-family in compartment id ${oci_identity_compartment.lab.id} where all {request.principal.type='aidataplatform'}",
  ] : [])
}
