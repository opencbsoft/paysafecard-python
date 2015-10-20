from paysafe import PaySafeCard

username = ''
password = ''

# create disposition example

paysafe = PaySafeCard(username, password)
paysafe.set_field('currency', 'GBP')
response = paysafe.confirm_merchant_data()
if response:
    print(response)
else:
    print('failed response')
paysafe.set_field('amount', '12.00')
paysafe.set_field('mtid', '52345678910123456789')
paysafe.set_field('merchantclientid', '1')
paysafe.set_field('okUrl', '')
paysafe.set_field('nokUrl', '')
paysafe.set_field('pnUrl', '')
paysafe.set_field('clientIp', '192.168.0.1')
paysafe.set_field('mid', '1000006446')
#response = paysafe.create_disposition()
#print(response)
#print(paysafe.get_url())
