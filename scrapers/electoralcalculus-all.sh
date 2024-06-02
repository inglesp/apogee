#!/bin/bash

for n in {0..12}; do
        ./scrapers/electoralcalculus.sh "$n" &
        sleep 10
done

