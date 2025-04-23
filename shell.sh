#!/bin/bash

echo "Running Script"
scp trainer.yml labels.txt zoro@10.20.184.23:/home/zoro/face_recon_model/3d/

# sshpass -p "@123" ssh zoro@10.20.184.23