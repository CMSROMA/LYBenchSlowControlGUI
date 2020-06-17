#!/bin/sh

echo "Turning ON LED"
echo 'C1:OUTP ON'>/dev/usbtmc0
echo 'C2:OUTP ON'>/dev/usbtmc0
