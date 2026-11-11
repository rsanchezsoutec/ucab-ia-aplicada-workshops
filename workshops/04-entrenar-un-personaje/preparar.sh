#!/usr/bin/env bash
# Revisa que el Spark tenga lo necesario para el lab 4 y deja la carpeta como repositorio git.
cd "$(dirname "$0")"
export PATH=/usr/local/cuda/bin:$PATH
ok=true
revisar() { if eval "$2" >/dev/null 2>&1; then echo "  ok      $1"; else echo "  FALTA   $1 · $3"; ok=false; fi; }

echo "Revisando el Spark…"
revisar "GPU visible (nvidia-smi)" "nvidia-smi" "avisa al facilitador"
revisar "CUDA (nvcc)" "nvcc --version" "avisa al facilitador"
revisar "Python 3" "python3 --version" "avisa al facilitador"
revisar "venv de Python" "python3 -m venv --help" "avisa al facilitador: falta python3-venv"
revisar "Cabeceras de Python (python3-dev)" \
  "python3 -c 'import os,sysconfig,sys; sys.exit(0 if os.path.exists(os.path.join(sysconfig.get_paths()[\"include\"],\"Python.h\")) else 1)'" \
  "avisa al facilitador: hay que instalar python3-dev"
revisar "git" "git --version" "avisa al facilitador"
revisar "Modelo del Spark en http://127.0.0.1:8080" "curl -sf http://127.0.0.1:8080/health" "avisa al facilitador: el alumno B lo necesita"
libre=$(df -Pk . | awk 'NR==2 {print int($4/1024/1024)}')
revisar "Espacio en disco (${libre} GB libres, hacen falta 25)" "[ ${libre:-0} -ge 25 ]" "libera espacio o avisa al facilitador"

if [ ! -d .git ]; then
  git init -q
  git add -A
  git -c user.name="workshop" -c user.email="workshop@example.com" commit -q -m "Estado inicial del lab 4"
fi
if $ok; then echo "Listo. Cada uno sigue con su rol en el README."; else echo "Hay cosas que faltan: avisa al facilitador antes de seguir."; fi
