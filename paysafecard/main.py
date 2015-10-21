import json

from suds import client
from ast import literal_eval
from suds.sudsobject import asdict


class PaySafeCard:

    log_data = []
    data = dict()

    def __init__(self, username, password, debug=True, test=True):
        self.debug = debug
        self.__reset()
        if self.__validate('username', username):
            self.data['username'] = username
        if self.__validate('password', password):
            self.data['password'] = password
        if test:
            self.data['url'] = 'https://soatest.paysafecard.com/psc/services/PscService?wsdl'
            self.data['redirect_url'] = 'https://customer.test.at.paysafecard.com/psccustomer/GetCustomerPanelServlet'
        else:
            self.data['url'] = 'https://soa.paysafecard.com/psc/services/PscService?wsdl'
            self.data['redirect_url'] = 'https://customer.cc.at.paysafecard.com/psccustomer/GetCustomerPanelServlet'
        self.__connect()

    def set_field(self, field, value):
        if self.__validate(field, value):
            self.data[field] = value

    def confirm_merchant_data(self):
        if not (self.data['username'] or self.data['password'] or self.data['currency']):
            self.__add_log('One of the required fields is missing', 'confirm_merchant')
            return False
        else:
            response = self.client.service.getMid(username=self.data['username'], password=self.data['password'], currency=self.data['currency'])
            json_response = self.__suds_to_json(response)
            if json_response['resultCode'] == 0 and json_response['errorCode'] == 0:
                self.data['mid'] = json_response['mid']
            else:
                return False
            return json_response

    def create_disposition(self):
        if not(self.data['username'] or self.data['password'] or self.data['mtid'] or self.data['amount'] or self.data['currency'] or self.data['okUrl']
               or self.data['nokUrl'] or self.data['merchantclientid'] or self.data['pnUrl'] or self.data['clientIp']):
            self.__add_log('One of the required fields is missing', 'create_disposition')
            return False
        if len(self.log_data) == 0:
            response = self.client.service.createDisposition(username=self.data['username'], password=self.data['password'], mtid=self.data['mtid'],
                                                         amount=self.data['amount'], currency=self.data['currency'], okUrl=self.data['okUrl'], nokUrl=self.data['nokUrl'],
                                                         merchantclientid=self.data['merchantclientid'], pnUrl=self.data['pnUrl'], clientIp=self.data['clientIp'])
            json_response = self.__suds_to_json(response)
            if json_response['resultCode'] == 0 and json_response['errorCode'] == 0:
                return json_response
            else:
                self.__add_log('Error '+str(json_response), 'create_disposition')
                return False
        else:
            return False

    def get_url(self):
        url = self.data['redirect_url'] +'?currency={0}&mtid={1}&amount={2}&mid={3}'.format(self.data['currency'], self.data['mtid'], self.data['amount'], self.data['mid'])
        return url

    def execute_debit(self, amount, close="1"):
        if not (self.data['username'] or self.data['password'] or self.data['mtid'] or self.data['amount'] or self.data['currency'] or self.data['close']):
            self.__add_log('One of the required fields is missing', 'execute_debit')
            return False
        if len(self.log_data) == 0:
            response = self.client.service.executeDebit(username=self.data['username'], password=self.data['password'], mtid=self.data['mtid'],
                                                        subId=self.data['subId'], amount=self.data['amount'], currency=self.data['currency'], close=self.data['close'])
            json_response = self.__suds_to_json(response)
            if json_response['resultCode'] == 0 and json_response['errorCode'] == 0:
                return True
            else:
                self.__add_log('Error '+str(json_response), 'create_disposition')
                return False

    def get_serial_numbers(self, mtid, currency, subid=None):
        self.set_field('mtid', mtid)
        self.set_field('currency', currency)
        if subid:
            self.set_field('subId', subid)
        if not (self.data['username'] or self.data['password'] or self.data['mtid'] or self.data['currency']):
            self.__add_log('One of the required fields is missing', 'get_serial_numbers')
            return False
        if len(self.log_data) == 0:
            response = self.client.service.getSerialNumbers(username=self.data['username'], password=self.data['password'],
                                                            mtid=self.data['mtid'], currency=self.data['currency'], subId=self.data['subId'])
            json_response = self.__suds_to_json(response)
            if json_response['resultCode'] == 0 and json_response['errorCode'] == 0:
                if json_response['dispositionState'] == 'S' or json_response['dispositionState'] == 'E':
                    return 'execute'
                elif json_response['dispositionState'] == 'O':
                    return 'completed'
                else:
                    self.__add_log('Error '+str(json_response), 'get_serial_numbers')
                    return False
            else:
                self.__add_log('Error '+str(json_response), 'get_serial_numbers')
                return False
        else:
            return False

    def get_debug(self):
        return str(self.data)

    def get_log(self):
        return str(self.log_data)

    def __recursive_asdict(self, d):
        """Convert Suds object into serializable format."""
        out = {}
        for k, v in asdict(d).items():
            if hasattr(v, '__keylist__'):
                out[k] = self.__recursive_asdict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(self.__recursive_asdict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out

    def __suds_to_json(self, data):
        return json.dumps(self.__recursive_asdict(data))

    def __validate(self, type, value):
        if type == '' and value == '':
            self.__add_log('error_validation', 'validate', 'type & value', '>>empty<<')
            return False
        if type == 'username':
            if not value:
                self.__add_log('username_empty', 'validate_username')
                return False
            elif len(value)<= 3:
                self.__add_log('username_length', 'validate_username', '>>hidden<<')
                return False
            else:
                return True
        elif type == 'password':
            if not value:
                self.__add_log('password_empty', 'validate_password')
                return False
            elif len(value)<= 5:
                self.__add_log('password_length', 'validate_password', '>>hidden<<')
                return False
            else:
                return True
        elif type == 'amount':
            if not value:
                self.__add_log('empty_amount', 'validate_amount')
                return False
            elif len(value)<= 3:
                self.__add_log('wrong_amount', 'validate_amount', value)
                return False
            elif ',' in value or '.' not in value:
                self.__add_log('dot_amount', 'validate_amount', value)
                return False
            else:
                amount_parts = value.split('.')
                if len(amount_parts)>2 or len(amount_parts[1])!= 2:
                    self.__add_log('null_amount', 'validate_amount', value)
                    return False
                else:
                    return True
        elif type == 'merchantclientid':
            if not value:
                self.__add_log('invalid_client_id', 'validate_clientId', value)
                return False
        elif type == 'currency':
            if len(value) != 3:
                self.__add_log('wrong_currency', 'validate_currency', value)
                return False
            else:
                return True
        elif type == 'shopId':
            if not value:
                self.__add_log('shopid_invalid', 'validate_shopId', value)
                return False
            if len(value) > 60:
                self.__add_log('shopid_oversize', 'validate_shopId', value)
                return False
            elif len(value) < 1:
                self.__add_log('shopid_undersize', 'validate_shopId', value)
                return False
            else:
                return True
        elif type == 'shopLabel':
            if not value:
                self.__add_log('shoplabel_invalid', 'validate_shopLabel', value)
                return False
            if len(value) > 60:
                self.__add_log('shoplabel_oversize', 'validate_shopLabel', value)
                return False
            elif len(value) < 1:
                self.__add_log('shoplabel_undersize', 'validate_shopLabel', value)
                return False
            else:
                return True
        elif type == 'mtid':
            if not value:
                self.__add_log('mtid_invalid', 'validate_mtid', value)
                return False
            if len(value) > 60:
                self.__add_log('mtid_oversize', 'validate_mtid', value)
                return False
            elif len(value) < 1:
                self.__add_log('mtid_undersize', 'validate_mtid', value)
                return False
            else:
                return True
        elif type == 'subId':
            return True
        elif type == 'close':
            if value not in ['0', '1']:
                self.__add_log('invalid_close', 'validate_close', value)
                return False
            else:
                return True
        else:
            if not type:
                self.__add_log('error_validation_type', 'validate_default')
                return False
            else:
                # the cases that aren't covered here are default to true
                return True

    def __reset(self):
        fields = ['username', 'password', 'mtid', 'clientIp', 'subId', 'merchantclientid', 'amount', 'currency', 'language', 'locale', 'close',
                  'mid', 'shopLabel', 'shopId', 'ok_url', 'nok_url', 'pn_url', 'dispositionRestrictions', 'dispositionState']
        for field in fields:
            self.data[field] = ''
        # default settings
        self.data['currency'] = 'EUR'
        self.data['close'] = '1'

    def __add_log(self, msg_code, call, call_params=None, result=None, log_type='error'):
        log_data = dict()
        log_data['msg_code'] = msg_code
        log_data['action'] = call
        if call_params:
            log_data['action_params'] = call_params
        if result:
            log_data['result'] = result
        log_data['type'] = log_type
        self.log_data.append(log_data)

    def __connect(self):
        self.client = client.Client(self.data['url'])

