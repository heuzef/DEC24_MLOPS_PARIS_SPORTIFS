# Créer une session Tmux qui expose les rapports HTML sur le port 8000
cd html
tmux new-session -d -s expose_drift_monitoring_reports "python -m http.server 8000"
