{{- define "train.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name }}
{{- end -}}

{{- define "model-pvc.fullname" -}}
{{- printf "%s-%s-pvc" .Release.Name .Chart.Name }}
{{- end -}}
