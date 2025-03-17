{{/*
Returns the correct namespace based on the environment.
*/}}
{{- define "miraculin.namespace" -}}
{{- if and .Values.setEnvVar.test (not .Values.setEnvVar.prod) -}}
{{ .Values.setEnvTest }}
{{- else if and (not .Values.setEnvVar.test) .Values.setEnvVar.prod -}}
{{ .Values.setEnvProd }}
{{- end -}}
{{- end -}}

{{/*
Returns environment-specific variables such as DB_HOST and DB_PORT.
*/}}
{{- define "miraculin.envVars" -}}
- name: DB_HOST
  value: "{{ ternary .Values.db.prod.host .Values.db.test.host .Values.setEnvVar.prod }}"
- name: DB_PORT
  value: "{{ ternary .Values.db.prod.port .Values.db.test.port .Values.setEnvVar.prod }}"
{{- end -}}

{{/*
Returns the correct nodePort based on the environment.
*/}}
{{- define "miraculin.nodePort" -}}
{{- if .Values.setEnvVar.prod -}}
{{ .Values.services.web.nodePort.prod }}
{{- else -}}
{{ .Values.services.web.nodePort.test }}
{{- end -}}
{{- end -}}
