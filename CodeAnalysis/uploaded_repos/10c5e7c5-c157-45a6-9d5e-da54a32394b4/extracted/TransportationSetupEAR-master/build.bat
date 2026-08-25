rem Start build....

pushd %PROJ_DIR%
set EMDCS_BUILD_DIR=C:\Raj\build
call %EMDCS_BUILD_DIR%\setargs.bat

ant -buildfile build.xml

rem End of execution
