#!/bin/bash

uvicorn "rubhew.main:create_app" --factory --reload 
