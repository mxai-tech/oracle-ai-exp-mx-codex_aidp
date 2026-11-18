# Infraestructura del taller en OCI Resource Manager

[Volver al tutorial](../README.md) · [Descargar el paquete Terraform](../Terraform.zip)

Esta configuración aprovisiona el entorno OCI del taller. Ejecútala mediante **Resource Manager** en la consola OCI. Los archivos de esta carpeta corresponden al paquete `Terraform.zip`; sus comentarios, descripciones y mensajes están traducidos al español. Se conservan los identificadores, las versiones y la lógica de infraestructura del original.

## Requisitos previos

- Cuenta OCI activa con acceso a Resource Manager y autorización para crear los recursos de este paquete, incluidos el compartment y las políticas en la tenancy.
- Región `us-chicago-1` suscrita, con AIDP, cuotas, capacidad y créditos disponibles para la cuenta. El código verifica que la región esté suscrita y `READY`, pero no garantiza los demás requisitos.
- Un compartment existente para alojar la stack, fuera del compartment temporal que creará Terraform.
- Acceso a la región principal de la tenancy para las operaciones IAM. La configuración descubre automáticamente esa región, que puede ser distinta de Chicago.

Resource Manager proporciona la autenticación de la ejecución. Este paso no requiere Terraform ni Python instalados en la computadora ni cargar una clave privada PEM. La API Key que usará después el plugin Ask AIDP es una configuración local independiente.

## Qué se creará

| Recurso | Configuración |
| --- | --- |
| Compartment | `lab_codex_aidp_rm`, con los valores predeterminados |
| Políticas del servicio AIDP | Una en la tenancy y otra en el compartment del laboratorio |
| Instancia AIDP | `lab-codex-aidp-rm` |
| Workspace inicial | `lab-validacao`, creado por la configuración de la instancia |
| Lakehouse 26ai | Opcional, deshabilitado de forma predeterminada |

La stack incluye una espera para la propagación inicial de las políticas. Las operaciones IAM usan la región principal de la tenancy.

Terraform **no crea** Spark Compute `labspark`, el esquema, el volumen, el CSV, los notebooks ni el job. Sigue el [tutorial principal](../README.md) para realizar esos pasos con Codex y Ask AIDP después de Apply.

Las políticas de este código conceden acceso al **servicio AIDP**, con condiciones sobre el principal y los recursos. No crean usuarios, grupos ni credenciales y no conceden al participante los permisos necesarios para ejecutar la stack. En una cuenta con acceso restringido, el administrador debe revisar esos permisos antes del taller.

## Parámetros

| Parámetro | Valor predeterminado | Orientación para el laboratorio |
| --- | --- | --- |
| `tenancy_ocid` | Sin valor predeterminado en Terraform | Revisa el OCID de tu tenancy completado en el formulario |
| `region` | `us-chicago-1` | Usa Chicago después de revisar disponibilidad y cuotas |
| `lab_name` | `lab-codex-aidp-rm` | Consérvalo en una cuenta de prueba individual o usa un nombre exclusivo |
| `workspace_name` | `lab-validacao` | Conserva el mismo nombre en los siguientes pasos |
| `enable_ai_features` | `false` | Déjalo desmarcado para los notebooks Spark |
| `iam_wait_seconds` | `90` | Espera inicial de IAM; acepta de 30 a 600 segundos |
| `lakehouse_database_name` | `LABAIDP` | Se usa solo si Lakehouse está habilitado |
| `lakehouse_admin_password` | `null` | Completa solo el campo protegido si habilitas Lakehouse |

El formulario oculta `tenancy_ocid` e `iam_wait_seconds` en el grupo de configuración automática. El nombre del compartment se deriva de `lab_name`, con los guiones sustituidos por guiones bajos.

Con `enable_ai_features=true`, el paquete crea Lakehouse 26ai con **2 ECPUs y 1 TB**, licencia incluida y autoscaling deshabilitado. Esto consume créditos adicionales. La contraseña está marcada como sensible, pero puede estar presente en el state; restringe el acceso a la stack. Esta opción no es necesaria para el laboratorio Spark.

## Crear la stack

1. Abre **Developer Services > Resource Manager > Stacks > Create stack** en la consola OCI.
2. Selecciona la opción de configuración propia y carga [Terraform.zip](../Terraform.zip). Carga ese ZIP interno, con los `.tf` en la raíz, en lugar del ZIP de todo el repositorio.
3. Si aparece el campo de directorio de trabajo, elige la raíz (`.`).
4. Selecciona **Terraform 1.5.x**, según el requisito de este paquete.
5. Aloja la stack en un compartment existente. No uses el compartment temporal creado por el propio laboratorio.
6. Revisa los parámetros de la tabla anterior y mantén Lakehouse deshabilitado.
7. Ejecuta **Plan**. Revisa los recursos y cualquier modificación o sustitución indicada.
8. Ejecuta **Apply** y sigue el job hasta su estado final.
9. Revisa la instancia AIDP en la consola, espera `ACTIVE` y guarda los siguientes outputs.

Si un intento falla, consulta el error y corrige **la misma stack**, conservando los parámetros y el state. Antes de volver a intentarlo, revisa qué recursos ya existen. No crees otra stack para administrar el mismo entorno.

## Outputs y siguiente paso

| Output | Uso |
| --- | --- |
| `aidp_instance_id` | OCID de la instancia para conectar el plugin |
| `region` | Región de la instancia |
| `workspace_name` | Nombre para identificar el workspace real |
| `compartment_id` | Identificador del compartment para revisión y limpieza |
| `home_region` | Región de las operaciones IAM |
| `lakehouse_id` | OCID del Lakehouse opcional o `null` |
| `console_url` | Enlace de AIDP en la región configurada |
| `next_step` | Recordatorio para crear Spark con Codex/Workbench |

Guarda también el nombre y el enlace de la stack. El siguiente paso del tutorial usa `aidp_instance_id`, `region` y `workspace_name` para conectar Ask AIDP y guardar `ambiente-lab.json` localmente.

`workspaceKey` y `clusterKey` no son outputs de esta stack. El plugin identifica el primero al conectar y guarda el segundo después de crear o reutilizar `labspark`.

## Cierre y eliminación

Ejecuta este paso solo después de terminar el taller y guardar los resultados que quieras conservar.

1. Exporta notebooks y evidencias. Finaliza los jobs y otras ejecuciones del laboratorio.
2. Detén el compute `labspark` de esta cuenta.
3. Revisa los datos y archivos administrados del entorno. Cuando haga falta, usa las opciones de eliminación en la consola AIDP antes de eliminar la instancia.
4. Abre **la misma stack**, revisa el impacto y ejecuta **Terraform actions > Destroy**.
5. Espera al estado final del job. Si no se puede eliminar el compartment, revisa los buckets y registros restantes, elimina solo los residuos de este laboratorio y repite Destroy.
6. Revisa los recursos restantes y el consumo de la cuenta en la consola. Elimina la stack solo después de completar Destroy y la verificación.

El state cubre los recursos declarados en este paquete. No incluye individualmente todos los objetos creados por el plugin ni todos los recursos internos generados por AIDP. Detener Spark o eliminar solo la stack no elimina toda la infraestructura. El state de esta variante pertenece a Resource Manager; no uses el `destroy.py` de otra variante local.

## Versiones y límites de validación

- Terraform requerido por el código: `~> 1.5.0`.
- Proveedor OCI: `9.11.0`.
- Proveedor Time: `~> 0.13.0`, fijado en `0.13.1` en el archivo de bloqueo incluido en el ZIP.

[VALIDACION.json](VALIDACION.json) conserva el registro histórico de pruebas estáticas del kit de origen, realizadas el 3 de noviembre de 2026 con Terraform CLI 1.5.7. Incluye `init`, `validate`, esquema y planes simulados. Declara que **no hubo Plan, Apply ni Destroy reales en OCI Resource Manager**. Estas pruebas no comprueban la elegibilidad de la cuenta, los permisos, las cuotas, la disponibilidad regional ni la aceptación de la configuración por la API. La fecha de ese registro corresponde al original, no a una nueva ejecución de las pruebas durante la traducción.

El paquete traducido conserva `.terraform.lock.hcl` del ZIP original. El código de infraestructura y los archivos traducidos del paquete coinciden con esta carpeta; el README interno adapta sus enlaces a la ubicación de extracción.

## Referencias oficiales

- [Estructura de configuraciones y autenticación en Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Concepts/terraformconfigresourcemanager.htm)
- [Versiones de Terraform en Resource Manager](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Reference/terraformversions.htm)
- [Recurso AIDP del proveedor OCI](https://docs.oracle.com/en-us/iaas/tools/terraform-provider-oci/latest/docs/r/ai_data_platform_ai_data_platform.html)
- [Modelos de cómputo de Autonomous Database](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/autonomous-compute-models.html)
