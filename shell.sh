#!/bin/bash

scp trainer.yml labels.txt Models/recognition.py sw@192.168.100.12:/Desktop/

sshpass -p "sw" ssh sw@192.168.100.12

