import requests
import json
import oauth2 as oauth
from oauth2_extended import SignatureMethod_HMAC_SHA256
import time
import argparse

class SalesOrderCreate():

    # Define the global variables
    def __init__(self):
        self.restlet_url = 'https://{netsuite_instance}.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=1033&deploy=1'
        self.realm = 'NETSUITE_INSTANCE'
        self.company = ''
        self.token_key = ''
        self.token_secret = ''
        self.consumer_key = ''
        self.consumer_secret = ''
        self.woocommerce_consumer_key = ''
        self.woocommerce_consumer_secret = ''
        self.woocommerce_orders_url = f'http://{company}.com/wp-json/wc/v3/orders/'


    def getWooCommerceOrder(self, order):
        
        woocommerce_url = self.woocommerce_orders_url+str(order)
        response = requests.get(woocommerce_url, auth=(self.woocommerce_consumer_key, self.woocommerce_consumer_secret))

        json_response = response.json()

        return json_response

    def convertStateCodeToState(self, state_code):

        states = {
            "AL" : "Alabama",
            "AK" : "Alaska",
            "AZ" : "Arizona",
            "AR" : "Arkansas",
            "CA" : "California",
            "CO" : "Colorado",
            "CT" : "Connecticut",
            "DL" : "Delaware",
            "DC" : "District of Columbia",
            "FL" : "Florida",
            "GA" : "Georgia",
            "HI" : "Hawaii",
            "ID" : "Idaho",
            "IL" : "Illinois",
            "IN" : "Indiana",
            "IA" : "Iowa",
            "KS" : "Kansas",
            "KY" : "Kentucky",
            "LA" : "Louisiana",
            "ME" : "Maine",
            "MD" : "Maryland",
            "MA" : "Massachusetts",
            "MI" : "Michigan",
            "MN" : "Minnesota",
            "MS" : "Mississippi",
            "MO" : "Missouri",
            "MT" : "Montana",
            "NE" : "Nebraska",
            "NV" : "Nevada",
            "NH" : "New Hampshire",
            "NJ" : "New Jersey",
            "NM" : "New Mexico",
            "NY" : "New York",
            "NC" : "North Carolina",
            "ND" : "North Dakota",
            "OH" : "Ohio",
            "OK" : "Oklahoma",
            "OR" : "Oregon",
            "PA" : "Pennsylvania",
            "RI" : "Rhode Island",
            "SC" : "South Carolina",
            "SD" : "South Dakota",
            "TN" : "Tennessee",
            "TX" : "Texas",
            "UT" : "Utah",
            "VT" : "Vermont",
            "VA" : "Virginia",
            "WA" : "Washington",
            "WV" : "West Virginia",
            "WI" : "Wisconsin",
            "WY" : "Wyoming"
        }

        state = states[state_code]

        return state

    def convertItemsToCode(self, sku):

        items = {
            "T00001-1" : [{'sku': 50, 'quantity': 1}], #50
            "T00001.2" : [{'sku': 52, 'quantity': 1}], #52
            "185-0004" : [{'sku': 1718, 'quantity':1}], #1718
            "T00001-1-2" : [{'sku': 1713, 'quantity': 1}], #1713
            "150-0008-1-1-1" : [{'sku': 1719, 'quantity':1}], #1719
            "150-0008-1-1" : [{'sku': 1720, 'quantity':1}], #1720
            "150-0008-1" : [{'sku': 1721, 'quantity':1}], #1721
            "150-0004" : [{'sku': 1104, 'quantity':1}], #1104
            "150-0008" : [{'sku': 1229, 'quantity':1}], #1229
            "theragun-g4" : [{'sku': 1243, 'quantity':1}], #1243
            "T00001-1-1" : [{'sku': 50, 'quantity': 1}], #50
            "T00001-2" : [{'sku': 50, 'quantity': 1}], #50
            "smart-accessories" : [{'sku': 51, 'quantity': 1}], #51
            "T00001" : [{'sku': 8, 'quantity':1}], #8
            "185-0007" : [{'sku': 1719, 'quantity':1}], #1719
            "Subscription" : [{'sku': 28, 'quantity':1}],
            "Subscription-36" : [{'sku': 1212, 'quantity':1}],
            "Shipping Income" : [{'sku': 49, 'quantity':1}]
        }

        item_code = items[sku]
        return item_code

    def configuredDate(self, date):

        split_date = date.split("-")
        
        configured_date = split_date[1]+"/"+split_date[2]+"/"+split_date[0]

        return configured_date

    def configureWooCommerceToNetSuite(self, order):

        # Initiate the payload as dictionary/json
        payload = {}
        order_data = self.getWooCommerceOrder(order)
        
        # print (order_data)
        # Begin assigning data to variables
        netsuite_customer_id = 2834777 # Mykola Zhurauskyy in SB1 | 2834777 in SB2
        po_number = order_data['id']
        date_created = self.configuredDate(order_data['date_created'][0:10])
        memo = order_data['order_key']
        shipping_address_1 = order_data['shipping']['address_1']
        shipping_address_2 = order_data['shipping']['address_2']
        shipping_city = order_data['shipping']['city']
        shipping_zip = order_data['shipping']['postcode']
        #shipping_state = self.convertStateCodeToState(order_data['shipping']['state'])
        shipping_state = order_data['shipping']['state']
        shipping_country = order_data['shipping']['country']

        # print("#"*20)
        # print(date_created)

        # Add header level items to the payload
        payload['netsuite_customer_id'] = netsuite_customer_id
        payload['purchase_order'] = po_number
        payload['date_created'] = date_created
        payload['memo'] = memo

        # Initialize shipping address
        payload['shipping_address'] = {}
        
        # Add shipping address
        payload['shipping_address']['shipping_address_1'] = shipping_address_1
        payload['shipping_address']['shipping_address_2'] = shipping_address_2
        payload['shipping_address']['shipping_zip'] = shipping_zip
        payload['shipping_address']['shipping_city'] = shipping_city
        payload['shipping_address']['shipping_state'] = shipping_state
        payload['shipping_address']['shipping_country'] = shipping_country 
        
        # Initialize item array
        payload['lines'] = []

        # Start iterating through lines
        for line_number in range(len(order_data['line_items'])):

            order_line = order_data['line_items'][line_number]

            line_skus = self.convertItemsToCode(order_line['sku'])

            print (line_skus)

            for line_item in range(len(line_skus)):
                line_payload = {}
                line_payload['sku'] = line_skus[line_item]['sku']
                line_payload['quantity'] = line_skus[line_item]['quantity']
                line_payload['rate'] = float(order_line['subtotal'])
                payload['lines'].append(line_payload)
                                
            # Initialize discounts payload - WooCommerce does not do line-level discounts

        for shipping_line in range(len(order_data['shipping_lines'])):
            
            shipping_line_payload = {}
            shipping_line_payload['sku'] = self.convertItemsToCode('Shipping Income')[shipping_line]['sku']
            shipping_line_payload['quantity'] = '1'
            shipping_line_payload['rate'] = float(order_data['shipping_lines'][shipping_line]['total'])

            print (shipping_line_payload)
            payload['lines'].append(shipping_line_payload)

        # Initialize global discounts
        payload['global_discounts'] = []

        for discount_line_number in range(len(order_data['coupon_lines'])):

            discount_line = order_data['coupon_lines'][discount_line_number]
            discount_line_payload = {}

            discount_line_payload['global_discount_code'] = discount_line['code']
            discount_line_payload['global_discount_rate_dollar'] = int(discount_line['discount'])

            payload['global_discounts'].append(discount_line_payload)

        # print('-'*20)
        print (json.dumps(payload, sort_keys=True, indent=4))

        return payload

    def postSalesOrder(self, order):

        # Get order data
        netsuite_payload = self.configureWooCommerceToNetSuite(order)

        token = oauth.Token(key=self.token_key, secret=self.token_secret)
        consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        realm = self.realm

        params = {
            'oauth_version' : "1.0",
            'oauth_nonce' : oauth.generate_nonce(),
            'oauth_timestamp' : str(int(time.time())),
            'oauth_token' : token.key,
            'oauth_consumer_key' : consumer.key
        }

        order_post_request = oauth.Request(method="POST", url = self.restlet_url, parameters=params)
        signature_method = SignatureMethod_HMAC_SHA256()
        order_post_request.sign_request(signature_method, consumer, token)
        header = order_post_request.to_header(realm)
        headery = header['Authorization'].encode('ascii','ignore')
        headerx = {"Authorization": headery, "Content-Type" : "application/json"}

        #print('-'*20)
        print (headerx)
        
        order_post = requests.post(self.restlet_url, headers = headerx, data = json.dumps(netsuite_payload))

        #print('-'*20)
        print(order_post.text)
        
        return order_post

if __name__ == "__main__":
    
    # Add parser to run from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--order', help='Enter Tonal order number')
    args = parser.parse_args()

    order_instance = SalesOrderCreate()
    my_order = order_instance.postSalesOrder(args.order)
    my_order = json.dumps(json.loads(my_order.text), indent=2)
