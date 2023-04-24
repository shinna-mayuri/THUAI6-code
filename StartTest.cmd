@echo off

start cmd /k RunServerForDebug
call C:\Anaconda3\Scripts\activate.bat C:\Anaconda3 
call conda activate ForTHUAI6
call conda env list
call RunPython
