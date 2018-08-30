set -x

convert -delay 1 ./*hitDistribution_*.png ./hitDistribution.gif 
convert -delay 1 ./*energySpectrum_*.png ./energyDistribution.gif 
convert -delay 1 ./*Residual5Param_cal*.png ./Residual5Param.gif 
convert -delay 1 ./*aserEnergyPulse_calo*.png ./laserEnergyPulse.gif 
