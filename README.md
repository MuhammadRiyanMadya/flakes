# flakes
<p align="center">
<p align="justify">
A control system package designed to automatically identify system characteristics from data sources like Excel, OPC UA server, etc. The parameters are valuable to designing proper controllers both with first principle controllers like PID or fuzzy logic or for the data-driven controller like MPC and ML 
  
## STUDY CASE: Extracting FOPTD parameters from step test data
<p align="center">
<img src="https://github.com/MuhammadRiyanMadya/flakes/blob/main/pic/Figure_1.png">
</p>
<p align="justify">
The most popular source of data is Excel. This package could extract data from Excel directly. In this demo, the file is
  
[Stepdata_process_2](https://github.com/MuhammadRiyanMadya/flakes/blob/main/pic/Stepdata_process_2.xlsx)
  
containing step test data of a controller in a chemical plant. This step test data has to be analyzed to get the process gain, process time, and time delay or dead time. These parameters can be quickly identified using this Python package.
</p>
<p align="center">
<img src="https://github.com/MuhammadRiyanMadya/flakes/blob/main/pic/Figure_2.png">
</p>
<p align="justify">
As we see above, the FOPTD parameters are extracted in highly accurate calculation by this Python program
