import time,network, micropg_lite, ntptime
from machine import Pin
from pimoroni_i2c import PimoroniI2C
#import ubinascii

# Issue #117 where neeed to sleep on startup otherwise might not boot
time.sleep(0.5)


### Sensor readings
sensor_reset_pin = Pin(9, Pin.OUT, value=True)
sensor_enable_pin = Pin(10, Pin.OUT, value=False)
boost_enable_pin = Pin(11, Pin.OUT, value=False)

PM1_UGM3                = 2
PM2_5_UGM3              = 3
PM10_UGM3               = 4
PM1_UGM3_ATHMOSPHERIC   = 5
PM2_5_UGM3_ATHMOSPHERIC = 6
PM10_UGM3_ATHMOSPHERIC  = 7
PM0_3_PER_LITRE         = 8
PM0_5_PER_LITRE         = 9
PM1_PER_LITRE           = 10
PM2_5_PER_LITRE         = 11
PM5_PER_LITRE           = 12
PM10_PER_LITRE          = 13

def wifi_connect(ssid, password):
    while wlan.isconnected() == False:
        wlan.connect(ssid, password)
        print('Connecting to wifi...')
        time.sleep(5)
    print("Connected to "+ ssid)
    return(None)
        
def UTC_DST_adj(): ### Daylight Savings Time accounted for: https://forum.micropython.org/viewtopic.php?f=2&t=4034
    inst = "CMU"
    now=time.time()
    if inst in ["NTU","IHEP"]:
        return(time.localtime(now+(3600*(8)))) ### No DST for China Standard Time +8
    elif inst == "TIFR":
        return(time.localtime(now+(3600*(5.5)))) ### No DST for India Standard Time +5:30
    else:
        dst_dates = [2025,9,2,2026,8,1,2027,14,7,2028,12,5,2029,11,4,2030,10,3]
        year = time.localtime()[0]
        dst_days = dst_dates.index(year) # get index of current year
        start_day = dst_dates[dst_days+1]   # get +1 from index for DST start day
        end_day = dst_dates[dst_days+2]   # get +2 from index for DST end day
        DST_start = time.mktime((year,3 ,start_day,1,0,0,0,0,0)) #Time of March change to DST
        DST_end = time.mktime((year,11,end_day,1,0,0,0,0,0)) #Time of November change to DST
        tz = 0
        if inst == "CMU":
            tz = -5   ### EST time zone
        elif inst == "TTU":
            tz = -6
        elif inst == "UCSB":
            tz = -8
        else:
            None
        if now < DST_start:               # we are before 2nd Sunday March
            return(time.localtime(now+(3600*tz)))
        elif now < DST_end:           # we are before 1st Sunday November
            return(time.localtime(now+(3600*(tz+1))))
        else:                            # we are after 1st Sunday November
            return(time.localtime(now+(3600*tz)))
  
def get_timestamp():
    lt=UTC_DST_adj()
    lt_str = []
#    lt = time.localtime(time.time())
    for item in lt:
        if item < 10:
            item = "0" + str(item)
        else:
            item = str(item)
        lt_str.append(item)
    local_time = lt_str[0]+'-'+lt_str[1]+'-'+lt_str[2]+' '+lt_str[3]+':'+lt_str[4]+':'+lt_str[5]
    return(local_time)

def particulates(particulate_data, measure):
    # covert deciliter to cubic meter to match ISO chart: 10,000 deciliters in 1 cubic meter
    multiplier = 10000 if measure >= PM0_3_PER_LITRE else 1
    return ((particulate_data[measure * 2] << 8) | particulate_data[measure * 2 + 1]) * multiplier

def get_particulates():
    pms_i2c = PimoroniI2C(14, 15, 100000)
    particulate_data = pms_i2c.readfrom_mem(0x12, 0x00, 32)
    pm0_5 = particulates(particulate_data, PM0_5_PER_LITRE), 
    pm1 = particulates(particulate_data, PM1_PER_LITRE), 
    pm5 = particulates(particulate_data, PM5_PER_LITRE)
    return([pm0_5, pm1, pm5])

def particulate_run():
    boost_enable_pin.value(True)
    sensor_enable_pin.value(True)
    print("Taking particulate counts...")
    time.sleep(30) ### allow at least 30 seconds before taking a reading per datasheet Page 9: https://www.mouser.co.uk/datasheet/2/737/4505_PMSA003I_series_data_manual_English_V2_6-2490334.pdf
    trial = 0
    pm_list = []
    trials = 40
    while trial < trials:
        #pm_list = get_particulates()
        trial_list = []
        for item in get_particulates():
            if isinstance(item, tuple):
                trial_list.append(int(max(item)))
            else:
                trial_list.append(int(item))
        pm_list.append(trial_list)
        trial += 1
        time.sleep(120/trials) ### evenly space measurements over 2 minutes
    boost_enable_pin.value(False)
    sensor_enable_pin.value(False)
    pm0_5 = []
    pm1 = []
    pm5 = []
    for item in pm_list:
        pm0_5.append(item[0])
        pm1.append(item[1])
        pm5.append(item[2])
    avg_list = [pm0_5, pm1, pm5]
    for item in avg_list:
        while 0 in item:
            item.remove(0)
    avgs = []
    for item in avg_list:
        try:
            avgs.append(round(sum(item)/len(item)))
        except ZeroDivisionError:
            avgs.append(0)
    return(str(avgs[0]), str(avgs[1]), str(avgs[2]))
            

### Initialization ###

### Database login
db_host = 'cmsmac04.phys.cmu.edu'
db_user = 'shipper'
db_password = 'hgcal'
db_database = 'hgcdb'
log_location = 'main_clean_room'

### Connect to wifi
ssid = 'CMU-DEVICE'
password = ""
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wifi_connect(ssid, password)
#print("MAC address is " + ubinascii.hexlify(wlan.config('mac')).decode())

### Sync with NTP
NTPerror = True
while NTPerror == True:
    try:
        ntptime.settime()
        NTPerror = False
    except:
        print("Syncing time with NTP...")
        NTPerror = True
        time.sleep(3)
print("Clock synced with NTP")    

def log_to_DB(ssid, password, db_host, db_user, db_password, db_database):
    start_time = time.ticks_ms()
    wifi_connect(ssid, password)
    try:
        print("Connecting to local DB...")
        conn = micropg_lite.connect(host=db_host,
                        user=db_user,
                        password=db_password,
                        database=db_database)
        print("Connected to local DB")
    except OSError:
        print("Unable to connect to DB, try again in 1 minute")
        return(60)
    cur = conn.cursor()
    log_timestamp = get_timestamp()
    pm0_5, pm1, pm5 = particulate_run()
    print("*****************************")
    print(log_timestamp)
    print('pm0_5: ' + pm0_5)
    print('pm1: ' + pm1)
    print('pm5: ' + pm5)
    print("*****************************")
    cur.execute("INSERT INTO particulate_counts (log_timestamp, log_location, prtcls_per_cubic_m_500nm, prtcls_per_cubic_m_1um, prtcls_per_cubic_m_5um) VALUES (%s, %s, %s, %s, %s)", [log_timestamp, log_location, pm0_5, pm1, pm5])
    conn.commit()
    conn.close()
    return(3600-((time.ticks_ms()-start_time)/1000))


while True:
    log_time = log_to_DB(ssid, password, db_host, db_user, db_password, db_database)
    time.sleep(log_time)
