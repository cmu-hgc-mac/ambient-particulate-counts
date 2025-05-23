# ambient-particulate-counts
How to set up a particulate matter sensor to automatically send ambient data to the local database. This kit was chosen initially for the [PMSA003I particulate matter sensor](https://www.mouser.co.uk/datasheet/2/737/4505_PMSA003I_series_data_manual_English_V2_6-2490334.pdf) and BME280 temperature and humidity sensor already attached to a Raspberry Pi Pico W microcontroller. However, [the temperature and humidity sensor data is not reliable due to close proximity to the microcontroller](https://github.com/pimoroni/enviro/issues/137). Even with programming a temperature bias, the humidity was found to not be accurate against known accurate values, possibly because relative humidity is inversely related to temperature. Instead, please see [the ambient temp and humidity project](https://github.com/cmu-hgc-mac/ambient-temp-humidity). The PMSA003I could be purchased and paired with many microcontrollers with wifi instead. However, [the Enviro Urban has additional circuitry that controls power to the PMSA003I](https://cdn.shopify.com/s/files/1/0174/1800/files/enviro_urban_schematic.pdf?v=1664452062), meaning that it only runs when desired instead of continuously. Other sensor options include the [SPS30](https://www.sparkfun.com/particulate-matter-sensor-sps30.html).

## Hardware
* [Pimoroni Enviro Urban](https://www.digikey.com/short/5h1jrvj5)
* Micro USB cable

## Setup
* Download Thonny: https://thonny.org/
* [Download the latest firmware](https://github.com/pimoroni/enviro/releases)
* Follow the [instructions under *Easy Mode*](https://github.com/pimoroni/enviro/blob/main/documentation/upgrading-firmware.md)
    * That is, hold in the BOOTSEL button while plugging the Pico W to the computer (or pressing Reset), and then move the U2f file to the window that pops up.
* In Thonny:
  * Click the Stop button or ctrl+c if needed.
  * Click on the text in the lower right corner. Select *Configure Interpreter...*
  * A window called *Thonny Options* should appear.
    * In the *Interpreter* tab, select *Micropython (Raspberry Pi Pico)* to run your code.
    * Select the USB port that is connected to the Pico W.
    * Select *OK* on the Thonny Options window.
  * In the Thonny main menu, ensure that *Files* under *View* is selected. This allows the user to view and modify files on the microcontroller.
  * Also in the main menu, go to Tools and select *Manage Packages...*
  * Install *micropg_lite*
  * Download main.py from this repository and save to the microcontroller.
  * Modify credentials in this file, such as wifi and database information.
  * Be sure to select the correct institution in the get_timestamp funtion to adjust for Daylight Savings Time.
    * When the microcontroller in not connected to a PC, time initializes to 01-01-2000.
  * Select the Run button under the main menu. Verify that valid particulate counts are being recorded in the local database.
    * CMU has a test database for this purpose. It is highly recommended to do the same.
* Stop running the Pico W and unplug from the PC. Connect the Pico W to external power. We use a power strip with a USB port.
* If the MAC address is needed, uncomment lines 4 and 147 initially. It is not recommended to take measurements reguarly with these lines not commented out.
