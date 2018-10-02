set -x

convert -delay 1 ./*hitDistribution_*.png ./hitDistribution.gif 
convert -delay 3 ./*energySpectrum_*.png ./energyDistribution.gif 
convert -delay 1 ./*Residual5Param_Cal*.png ./Residual5Param.gif 
convert -delay 1 ./*aserEnergyPulse_calo*.png ./laserEnergyPulse.gif 
