#pragma comment (lib, "Dbghelp.lib")
#pragma comment(lib, "Ws2_32.lib")

#include <iostream>
#include <windows.h>
#include <DbgHelp.h>
#include <TlHelp32.h>
#include <wchar.h>
#include <sstream>

bool IsElevated();
DWORD getLsassPid();
bool SetPrivilege();
