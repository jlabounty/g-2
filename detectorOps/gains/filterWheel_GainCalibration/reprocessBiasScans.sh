
root -l -b -q FWanalysis.C\(\"Results_FW_28043_28050_AllScans.root\",120,\"original.root\"\) | tee biasVoltageGains_original.txt
root -l -b -q FWanalysis.C\(\"Results_FW_28051_28058_AllScans.root\",120,\"plusPoint1.root\"\) | tee biasVoltageGains_plusPoint1.txt
root -l -b -q FWanalysis.C\(\"Results_FW_28059_28066_AllScans.root\",120,\"minusPoint1.root\"\) | tee biasVoltageGains_minusPoint1.txt
root -l -b -q FWanalysis.C\(\"Results_FW_28067_28074_AllScans.root\",120,\"plusPoint2.root\"\) | tee biasVoltageGains_plusPoint2.txt
root -l -b -q FWanalysis.C\(\"Results_FW_28075_28082_AllScans.root\",120,\"minusPoint2.root\"\) | tee biasVoltageGains_minusPoint2.txt
root -l -b -q FWanalysis.C\(\"Results_FW_28083_28090_AllScans.root\",120,\"originalEnd.root\"\) | tee biasVoltageGains_originalEnd.txt

echo " "
echo "All done!"
