@echo off
REM Author: Jospaul Mahajan Prakash
REM Company: Infosys Limited

set ALMUSERNAME=jprakash
set ALMPASSWORD=Infosys_123
set HOST=S4800POS213
set OUTPUTTYPE=tf
set ITERATION=1
set RUNIDLIST=191908,191912,191917,191920,191924,191926,191932,191933,191935,191936,191939,191941

python .\RegRepErrLog-py3.6\__main__.py -u %ALMUSERNAME% -p %ALMPASSWORD% -h %HOST% -o %OUTPUTTYPE% -i %ITERATION%