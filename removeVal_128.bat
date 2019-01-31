@echo off

del /S /Q \\entlr001\Parameters\*

echo p_ReceiptCM > \\entlr001\Parameters\Receipt_CM.dat
echo p_ReceiptRT > \\entlr001\Parameters\Receipt_RT.dat
echo p_ReceiptDef > \\entlr001\Parameters\Receipt_Def.dat
