
# Check the environment, test or prod.

{{- define "storage.namespace" -}}
{{- if and .Values.setEnvVar.test (not .Values.setEnvVar.prod) -}}
{{ .Values.setEnvTest }}
{{- else if and (not .Values.setEnvVar.test) .Values.setEnvVar.prod -}}
{{ .Values.setEnvProd }}

{{- end -}}
{{- end -}}
