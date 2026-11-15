@echo off
echo ======================================================================
echo AgriAI Multi-Input Model Retraining & Random Dataset Generation
echo ======================================================================
cd /d "%~dp0"
python ml-service/training/train_all_synthetic.py
echo.
echo All models successfully generated and saved to ml-service/models!
pause

