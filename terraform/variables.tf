variable "tenancy_ocid" {
  type        = string
  description = "OCID de la tenancy de prueba del participante."
  validation {
    condition     = can(regex("^ocid1[.]tenancy[.]", var.tenancy_ocid))
    error_message = "Indica el OCID de una tenancy."
  }
}

variable "region" {
  type        = string
  default     = "us-chicago-1"
  description = "Región suscrita con AIDP disponible y cuota en la cuenta de prueba."
}

variable "lab_name" {
  type        = string
  default     = "lab-codex-aidp-rm"
  description = "Prefijo exclusivo para este entorno temporal."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,39}$", var.lab_name))
    error_message = "Usa de 3 a 40 caracteres: letras minúsculas, números y guiones; comienza con una letra."
  }
}

variable "workspace_name" {
  type    = string
  default = "lab-validacao"
  validation {
    condition     = length(trimspace(var.workspace_name)) > 0
    error_message = "Indica un nombre de workspace."
  }
}

variable "iam_wait_seconds" {
  type    = number
  default = 90
  validation {
    condition     = var.iam_wait_seconds >= 30 && var.iam_wait_seconds <= 600
    error_message = "Usa entre 30 y 600 segundos para la propagación inicial de IAM."
  }
}

variable "enable_ai_features" {
  type        = bool
  default     = false
  description = "Opcional: crea Lakehouse 26ai con 2 ECPUs y 1 TB y lo asocia a AIDP. No se necesita para los tres notebooks; consume créditos adicionales."
}

variable "lakehouse_admin_password" {
  type        = string
  default     = null
  sensitive   = true
  description = "Solo con enable_ai_features=true. Completa el campo protegido de Resource Manager, nunca el ZIP."
}

variable "lakehouse_database_name" {
  type    = string
  default = "LABAIDP"
  validation {
    condition     = can(regex("^[A-Za-z][A-Za-z0-9]{0,13}$", var.lakehouse_database_name))
    error_message = "Usa de 1 a 14 caracteres alfanuméricos, comenzando con una letra."
  }
}
