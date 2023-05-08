@echo off

:: 添加 --cl 参数，程序运行时将自动识别命令行参数，并自动连接server
start cmd /k win64\Client.exe --cl --playbackFile .\video.thuaipb --playbackSpeed 4