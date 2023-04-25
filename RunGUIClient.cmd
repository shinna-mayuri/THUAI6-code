@echo off

:: 添加 --cl 参数，程序运行时将自动识别命令行参数，并自动连接server
start cmd /k win64\Client.exe --port 8888 --characterID 0 --type 1 --occupation 1 

start cmd /k win64\Client.exe --port 8888 --characterID 4 --type 2 --occupation 1
:: characterID > 2023时是观战Client，否则是正常Client
