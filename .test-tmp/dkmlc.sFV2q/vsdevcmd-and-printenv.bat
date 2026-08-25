@SET TEMP=C:\RD\DVV_ST~1\DSVSTR~1\TEST-T~1\DKMLC~1.SFV
@CALL "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\Common7\Tools\VsDevCmd.bat" %*
@SET _VSERR=%ERRORLEVEL%
if %_VSERR% neq 0 (
echo.
echo.FATAL: VsDevCmd.bat failed to find a Visual Studio compiler.
echo.
exit /b %_VSERR%
)
set > "C:\RD\DVV_ST~1\DSVSTR~1\TEST-T~1\dkmlc.sFV2q\vcvars.txt"
