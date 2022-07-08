# Script to monitor and read temperatures from Honeywell EvoHome Web API
**An xlsx file is added with the possibility to analyse the generated data**

## References:
- https://evohome-client.readthedocs.io/en/latest/api1/index.html
- https://international.mytotalconnectcomfort.com/Account/Login?task=timeout
- https://github.com/PieterVO/EvohomeTemperature

## Issues:
At certain moments the connection is timed-out. Therefore it needs to be reinitialised. This causes separate output files to be produced. Preferable solutions are found to:
- prevent the connection to timeout (other people experienced this as well)
- keep writing in the same output file