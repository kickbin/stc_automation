'''
Programmer Reference online
http://kms.spirentcom.com/CSC/STC%20Programmers%20Ref_WebHelp/WebHelp/Default.htm
Object references online
http://kms.spirentcom.com/CSC/pabtech/stc-automation-html/index.htm
'''
# This loads the TestCenter library.

from StcPython import StcPython
stc = StcPython()

def init():
    stc.log("INFO", "Starting Test")
    # This line will show the TestCenter commands on stdout
    stc.config("automationoptions", logto="stdout", loglevel="INFO")
    #loglevel options: "INFO", "WARN", "ERROR", "FATAL"
    # Retrieve and display the current API version.
    print("SpirentTestCenter system version:\t", {stc.get("system1", "version")})

    # Physical topology
    szChassisIp = "10.108.8.20"
    port_1_loc = "//%s/%s/%s" % ( szChassisIp, 8, 11) # Only 2 ports are used to test, reserve 4 ports to change mode
    port_2_loc = "//%s/%s/%s" % ( szChassisIp, 8, 12)
    # port_3_loc = "//%s/%s/%s" % ( szChassisIp, 1, 13)
    # port_4_loc = "//%s/%s/%s" % ( szChassisIp, 1, 14)

    # Create the root project object
    print("Creating project ...")
    hProject = stc.create("project")

    # Create ports
    print("Creating ports ...")
    port_1 = stc.create("port", under=hProject, location=port_1_loc, useDefaultHost=False)
    port_2 = stc.create("port", under=hProject, location=port_2_loc, useDefaultHost=False)

    def change_port_speed(LineSpeed):
    # MX2-10G-S16 ports set port speed:
    # LineSpeed options "SPEED_1G" or "SPEED_10G"
        print("changing speed to ", {LineSpeed})

        mx2_10G_port_1 = stc.create("Ethernet10GigFiber", under=port_1, \
                   LineSpeed=LineSpeed)

        mx2_10G_port_2= stc.create("Ethernet10GigFiber", under=port_2, \
                   LineSpeed=LineSpeed)

        stc.config(port_1, **{"ActivePhy-targets": [mx2_10G_port_1]})
        stc.config(port_2, **{"ActivePhy-targets": [mx2_10G_port_2]})

        # Attach ports.
        # Connects to chassis, reserves ports and sets up port mappings all in one step.
        # By default, connects to all previously created ports.
        print("Attaching ports ", {port_1_loc}, {port_2_loc})
        stc.perform("AttachPorts")

        # Apply the configuration.
        print("Apply configuration")
        stc.apply()

        # Show interface line speed status
        ports = [port_1, port_2]
        for port in ports:
            hPortSpeed = stc.get(port, "activephy")
            line_speed_status = stc.get(hPortSpeed, "LineSpeedStatus")
            print(port, " Line Speed : ", line_speed_status)

    change_port_speed("SPEED_1G")
    change_port_speed("SPEED_10G")
    change_port_speed("SPEED_1G")

    # Disconnect from chassis, release ports, and reset configuration.
    print( "Release ports and disconnect from chassis" )
    stc.perform('chassisDisconnectAll')
    stc.perform('resetConfig', createnewtestsessionid=0)

    # Delete configuration
    print( "Deleting project" )
    stc.delete(hProject)

    stc.log("INFO", "Ending Test")