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
    SPEED = "SPEED_2500M"
    # AlternateSpeeds options: "SPEED_10G" "SPEED_5G" "SPEED_2500M" "SPEED_1G" "SPEED_100M"
    AUTO_NEG = "TRUE"
    # AUTO_NEG options: "TRUE" "FALSE"

    stc.log("INFO", "Starting Test")
    # This line will show the TestCenter commands on stdout
    stc.config("automationoptions", logto="stdout", loglevel="ERROR")
    #loglevel options: "INFO", "WARN", "ERROR", "FATAL"
    # Retrieve and display the current API version.
    print("SpirentTestCenter system version:\t", {stc.get("system1", "version")})

    # Physical topology
    szChassisIp = "10.226.44.151"
    port_1_loc = "//%s/%s/%s" % ( szChassisIp, 1, 15) # Only 2 ports are used to test, reserve 4 ports to change mode
    port_2_loc = "//%s/%s/%s" % ( szChassisIp, 1, 16)
    # port_3_loc = "//%s/%s/%s" % ( szChassisIp, 1, 13)
    # port_4_loc = "//%s/%s/%s" % ( szChassisIp, 1, 14)

    # Create the root project object
    print("Creating project ...")
    hProject = stc.create("project")

    # Create ports
    print("Creating ports ...")
    port_1 = stc.create("port", under=hProject, location=port_1_loc, useDefaultHost=False)
    port_2 = stc.create("port", under=hProject, location=port_2_loc, useDefaultHost=False)

    # Configure physical interface.
    #hPortTxCopperInterface = stc.create("EthernetCopper",  under=port_1)


    port_options_dict =  {"PerformanceMode":"STC_MGIG", \
        "AdvertiseIEEE":"TRUE", \
           "AdvertiseNBASET":"TRUE", \
           "AutoNegotiation": "TRUE", \
           "FlowControl":"FALSE", \
           "Duplex":"FULL", \
           "IgnoreLinkStatus":"FALSE", \
           "DataPathMode":"NORMAL", \
           "Mtu":"1500", \
           "ForwardErrorCorrection":"TRUE", \
           "CustomFecChange":"0", \
           "CustomFecMode":"KR_FEC"}


    if SPEED == "SPEED_10G":
        port_options_dict["AlternateSpeeds"] = "SPEED_10G"
    elif SPEED == "SPEED_5G":
        port_options_dict["AlternateSpeeds"] = "SPEED_5G"
    elif SPEED == "SPEED_2500M":
        port_options_dict["AlternateSpeeds"] = "SPEED_2500M"
    elif SPEED == "SPEED_1G":
        port_options_dict["AlternateSpeeds"] = "SPEED_1G"
    elif SPEED == "SPEED_100M":
        port_options_dict["AlternateSpeeds"] = "SPEED_100M"

    if AUTO_NEG == "FALSE":
        port_options_dict["AutoNegotiation"] = "FALSE"

    # FX2-10G-S16 port config
    fx2_10G_port_1 = stc.create("Ethernet10GigFiber", under=port_1, \
               **port_options_dict)

    fx2_10G_port_2= stc.create("Ethernet10GigFiber", under=port_2, \
               **port_options_dict)


    stc.config(port_1, **{"ActivePhy-targets": [fx2_10G_port_1]})
    stc.config(port_2, **{"ActivePhy-targets": [fx2_10G_port_2]})


    # Retrieve the generator and analyzer objects.
    hGenerator = stc.get(port_1, "children-Generator")
    hAnalyzer = stc.get(port_2, "children-Analyzer")

    # Create a stream block.
    print("Configuring stream block ...")
    hStreamBlock = stc.create("streamBlock", under=port_1, insertSig=True, \
                              frameConfig="", frameLengthMode="FIXED", \
                              maxFrameLength=1200, FixedFrameLength=256)

    # Add an EthernetII Protocol Data Unit (PDU).
    print("Adding headers")
    hEthernet  = stc.create("ethernet:EthernetII", under=hStreamBlock, \
                            name="sb1_eth", srcMac="00:00:20:00:00:00", \
                            dstMac="00:00:00:00:00:00")

    # Use modifier to generate multiple streams.
    print("Creating Modifier on Stream Block ...")
    hRangeModifier = stc.create("RangeModifier", \
          under=hStreamBlock, \
          ModifierMode="DECR", \
          Mask="00:00:FF:FF:FF:FF", \
          StepValue="00:00:00:00:00:01", \
          Data="00:00:10:10:00:01", \
          RecycleCount=20, \
          RepeatCount=0, \
          DataType="NATIVE", \
          EnableStream=True, \
          Offset=0, \
          OffsetReference="sb1_eth.dstMac")

    # Display stream block information.
    print("\n\nStreamBlock information")

    dictStreamBlockInfo = stc.perform("StreamBlockGetInfo", StreamBlock=hStreamBlock)

    for szName in dictStreamBlockInfo:
        print("\t", {szName}, "\t", {dictStreamBlockInfo[szName]})

    print("\n\n")


    # Configure generator.
    print("Configuring Generator")
    hGeneratorConfig = stc.get(hGenerator, "children-GeneratorConfig")

    stc.config(hGeneratorConfig, \
              DurationMode="CONTINUOUS", \
              BurstSize=1, \
              Duration=30, \
              LoadMode="FIXED", \
              FixedLoad=90, \
              LoadUnit="PERCENT_LINE_RATE", \
              SchedulingMode="PORT_BASED")

    # Analyzer Configuration.
    print("Configuring Analyzer")
    hAnalyzerConfig = stc.get(hAnalyzer, "children-AnalyzerConfig")

    # Attach ports.
    # Connects to chassis, reserves ports and sets up port mappings all in one step.
    # By default, connects to all previously created ports.
    print("Attaching ports ", {port_1_loc}, {port_2_loc})
    stc.perform("AttachPorts")

    # Apply the configuration.
    print("Apply configuration")
    stc.apply()

    # Subscribe to realtime results.
    print("Subscribe to results")
    hAnaResults = stc.subscribe(Parent=hProject, \
                ConfigType="Analyzer", \
                resulttype="AnalyzerPortResults",  \
                filenameprefix="Analyzer_Port_Results")

    hGenResults = stc.subscribe(Parent=hProject, \
                ConfigType="Generator", \
                resulttype="GeneratorPortResults",  \
                filenameprefix="Generator_Port_Counter", \
                Interval=2)

    # Configure Capture.
    ENABLE_CAPTURE = False

    if ENABLE_CAPTURE:
        print("\nStarting Capture...")

        # Create a capture object. Automatically created.
        hCapture = stc.get(port_2, "children-capture")
        stc.config(hCapture, mode="REGULAR_MODE", srcMode="TX_RX_MODE")
        stc.perform("CaptureStart", captureProxyId=hCapture)

    # Apply configuration.
    print("Apply configuration")
    stc.apply()

    # Save the configuration as an XML file. Can be imported into the GUI.
    # print("\nSave configuration as an XML file.")
    # stc.perform("SaveAsXml")

    # Start the analyzer and generator.
    print("Start Analyzer")
    stc.perform("AnalyzerStart", AnalyzerList=hAnalyzer)
    print( "Current analyzer state ", {stc.get(hAnalyzer, "state")} )

    print("Start Generator")
    stc.perform("GeneratorStart", GeneratorList=hGenerator)
    print( "Current generator state",  {stc.get(hGenerator, "state")} )

    print("Wait 20 seconds ...")
    stc.sleep(20)

    print("Wait until generator stops ...")
    test_state = stc.waitUntilComplete(timeout=100)


    print( "Current analyzer state ", {stc.get(hAnalyzer, "state")} )
    print( "Current generator state ", {stc.get(hGenerator, "state")} )
    print("Stop Analyzer")

    # Stop the generator.
    stc.perform("GeneratorStop", GeneratorList=hGenerator)

    # Stop the analyzer.
    stc.perform("AnalyzerStop", AnalyzerList=hAnalyzer)



    # Display some statistics.

    # Show interface line speed status
    ports = [port_1, port_2]
    for port in ports:
        hPortSpeed = stc.get(port, "activephy")
        line_speed_status = stc.get(hPortSpeed, "LineSpeedStatus")
        print(port, " Line Speed : ", line_speed_status)

    # Example of Direct-Descendant Notation ( DDN ) syntax. ( DDN starts with an object reference )
    print( "Frames Counts:" )
    print( "\tSignature Frames Generated:", {stc.get("%s.GeneratorPortResults(1)" % hGenerator, "GeneratorSigFrameCount")} )
    print("\tSignature Frames Received: ", {stc.get("%s.AnalyzerPortResults(1)" % hAnalyzer, "sigFrameCount")})
    print("\tFrames Generated:", {stc.get("%s.GeneratorPortResults(1)" % hGenerator, "GeneratorFrameCount")})
    print("\tTotal Frames Received: ", {stc.get("%s.AnalyzerPortResults(1)" % hAnalyzer, "TotalFrameCount")})
    print( "\tTotal frame count: ", {stc.get("%s.AnalyzerPortResults(1)" % hAnalyzer, "totalFrameCount")} )
    print("\tFCS frame count: ", {stc.get("%s.AnalyzerPortResults(1)" % hAnalyzer, "FcsErrorFrameCount")})
    print( "\tDropped frames: ", {stc.get("%s.AnalyzerPortResults(1)" % hAnalyzer, "DroppedFrameCount")} )

    # Example of Descendant-Attribute Notation ( DAN ) syntax. ( using explicit indeces )
    print( "\tMinFrameLength: ", {stc.get(port_2, "Analyzer(1).AnalyzerPortResults(1).minFrameLength")} )
    # Notice indexing is not necessary since there is only 1 child.
    print( "\tMaxFrameLength: ", {stc.get(port_2, "Analyzer.AnalyzerPortResults.maxFrameLength")} )

    if ENABLE_CAPTURE:
        from time import gmtime, strftime
        print( strftime("%Y-%m-%d %H:%M:%S", gmtime()), " Retrieving Captured frames..." )

        stc.perform("CaptureStop", captureProxyId=hCapture)

        # Save captured frames to a file.
        stc.perform("CaptureDataSave", captureProxyId=hCapture, FileName="capture.pcap", \
                    FileNameFormat="PCAP", IsScap=False)

        print( "Captured frames:\t", stc.get(hCapture, "PktCount") )


    # Unsubscribe from results
    print( "Unsubscribe results ..." )
    stc.unsubscribe(hAnaResults)
    stc.unsubscribe(hGenResults)

    # Disconnect from chassis, release ports, and reset configuration.
    print( "Release ports and disconnect from chassis" )
    stc.perform('chassisDisconnectAll')
    stc.perform('resetConfig', createnewtestsessionid=0)

    # Delete configuration
    print( "Deleting project" )
    stc.delete(hProject)

    stc.log("INFO", "Ending Test")

    return test_state