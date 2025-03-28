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
{{- if .Values.db }}
- name: DB_HOST
  value: "{{ ternary .Values.db.prod.host .Values.db.test.host .Values.setEnvVar.prod }}"
- name: DB_PORT
  value: "{{ ternary .Values.db.prod.port .Values.db.test.port .Values.setEnvVar.prod }}"
{{- end }}
{{- end }}
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



{{/*
Dynamically generate environment variables for a service if defined
*/}}
{{- define "miraculin.envDependencies" -}}
{{- with .dependencies }}
{{- range $key, $value := . }}
- name: {{ $key }}
  value: {{ $value | quote }}
{{- end }}
{{- end }}
{{- end }}


{{/*
Returns environment-specific DB secrets for storage service
*/}}
{{- define "miraculin.storageSecrets" -}}
- name: DB_NAME
  valueFrom:
    secretKeyRef:
      name: db-secrets
      key: db_name
- name: DB_USERNAME
  valueFrom:
    secretKeyRef:
      name: db-secrets
      key: db_username
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secrets
      key: db_password
{{- end }}



