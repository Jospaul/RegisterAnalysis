@echo off

del /S /Q \\entlr005\Parameters\4028\*

echo p_ReceiptCM > \\entlr005\Parameters\4028\Receipt_CM.dat
echo p_ReceiptRT > \\entlr005\Parameters\4028\Receipt_RT.dat
echo p_ReceiptDef > \\entlr005\Parameters\4028\Receipt_Def.dat
