@echo off
echo 🚀 OPRYXX FULL STACK VERIFICATION
echo ================================

echo.
echo 📋 Running comprehensive test suite...
python test_full_stack_verification.py

echo.
echo 🔧 Validating GUI settings and options...
python gui_settings_validator.py

echo.
echo 🖥️ Testing unified GUI components...
python UNIFIED_FULL_STACK_GUI.py --test-mode

echo.
echo ✅ VERIFICATION COMPLETE!
echo Check test_results.json for detailed results
pause