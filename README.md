Paysafecard-python
==================

A class that implements the classic payment function of http://www.paysafecard.com

================================
## Instalation:
```
pip install paysafecard
```
## Example usage
Create the disposition and if it is successfull then redirect to the url.
```
from paysafecard.main import PaySafeCard
paysafe = PaySafeCard(username="", password="", debug=True, test=True)
paysafe.set_field('currency', 'EUR')
paysafe.set_field('amount', '10.00')
paysafe.set_field('mtid', 'transaction-id')
paysafe.set_field('merchantclientid', 'user-id')
paysafe.set_field('mid', 'currency-id')
paysafe.set_field('clientIp', '192.168.0.1')
paysafe.set_field('okUrl', '')
paysafe.set_field('nokUrl', '')
paysafe.set_field('pnUrl', '')
if paysafe.create_disposition():
    redirect_url = paysafe.get_url()
else:
    return False
```
After the client enters the required information you may have 2 cases one on the pnurl other to the okurl this function ensures that the amount was taken from paysafe to your account.
```
from paysafecard.main import PaySafeCard
paysafe = PaySafeCard(username='', password='', debug=True, test=True)
paysafe.set_field('amount', '10.00')
response = paysafe.get_serial_numbers('currency-id', 'EUR')
if response:
    if response == 'execute':
        if paysafe.execute_debit('10.00'):
            return True
        else:
            return False
    else:
        return False
else:
    return False
```