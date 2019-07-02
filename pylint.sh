#!/bin/bash

FILES=rri.py
   

 # Statische Codeanalyse durchführen
pylint3 --rcfile=pylint.rc --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
    $FILES >pylint.log || echo "INFO: Statische Codeanalyse hat Fehler gefunden"
    
pylint3 --rcfile=pylint.rc -E $FILES