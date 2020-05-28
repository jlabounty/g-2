def main():
  print('BEGIN_PROLOG')
  print('channel_status : {')
  for i in range(1,25):
    print('\tcalo'+str(i)+ ' : {')
    print('\tglobal : 1')
    for j in range(0,54):
      print('\t\txtal'+str(j)+' : 1')
    print('\t}')
  print('}')
  print('END_PROLOG')

main()
