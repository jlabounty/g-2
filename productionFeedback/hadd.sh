set -x

ding=$(ls ./*root | grep -v 'result')
str=echo $ding

#str3="hadd -T -f result_histOnly.root $ding"
#eval $str3

str2="hadd -f result.root $ding"
eval $str2
