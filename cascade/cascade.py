#!/usr/bin/env python3
"""
Class to interface with the Cascade API, provided by Inty
"""

# Standard Libraries
import logging
import http.client

# 3rd party packages
import requests

class CascadeAPI():
    """
    Class to interface with the Cascade API, provided by Inty.
    """
    def __init__(self, username: str, password: str, url: str='https://api.cascadeportal.com', debug: bool = False):
        """
        Initialises the CascadeAPI class
        """
        if debug:
            http.client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

        self.session = requests.session()
        self.session.headers.update({'X-Username': username})
        self.session.headers.update({'X-Password': password})
        self.session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        self.url = url
    
    def __sendget(self, endpoint: str, params: dict = {}) -> requests.Response:
        """
        Wrapper to send a get request and raise any errors
        PARAMETERS:
            endpoint: str. The endpoint to request, i.e. '/customers'
            params: dict. OPTIONAL. Any parameters in key value pairs. Defaults to {}.
        """
        # Check if endpoint starts with a /, or add one
        if not endpoint[0] == '/':
            endpoint = '/' + endpoint
        # Send the request
        response = self.session.get(self.url + endpoint, params=params)
        # If any errors, raise an exception
        response.raise_for_status()
        return response
    
    def __sendpost(self, endpoint: str, data: dict = None) -> requests.Response:
        """
        Wrapper to send a POST request and raise any errors
        PARAMETERS:
            endpoint: str. The endpoint to post to, i.e. '/customers'
            data: dict. The data to be sent in the HTTP request.
        """
        # Check if endpoint starts with a /, or add one
        if not endpoint[0] == '/':
            endpoint = '/' + endpoint
        # Send the request
        response = self.session.post(self.url + endpoint, json=data)
        # If any errors, raise an exception
        response.raise_for_status()
        return response
    
    def __senddelete(self, endpoint: str) -> requests.Response:
        """
        Wrapper to send a DELETE request and raise any errors
        PARAMETERS:
            endpoint: str. The endpoint to post to, i.e. '/customers'
        """
        # Check if endpoint starts with a /, or add one
        if not endpoint[0] == '/':
            endpoint = '/' + endpoint
        # Send the request
        response = self.session.delete(self.url + endpoint)
        # If any errors, raise an exception
        response.raise_for_status()
        return response
    
    def get_all_customers(self) -> list:
        """
        Get a list of all customers.
        """
        return self.__sendget('/Customers').json()
    
    def get_customer(self, primarydomain: str) -> dict:
        """
        Retrieve a single customer details
        PARAMETERS:
            primarydomain: Customer's primary domain
        """
        return self.__sendget(f'/Customers/{primarydomain}').json()
    
    def get_customer_tenant(self, primarydomain: str) -> dict:
        """
        Retrieve information about the Microsoft tenant for the customer
        PARAMETERS:
            primarydomain: Customer's primary domain
        """
        return self.__sendget(f'/customers/{primarydomain}/MicrosoftTenantAssociation').json()

    def get_customer_mca(self, primarydomain: str) -> dict:
        """
        Retrieve information about the Microsoft tenant for the customer
        PARAMETERS:
            primarydomain: Customer's primary domain
        """
        return self.__sendget(f'/customers/{primarydomain}/McaAcceptance').json()
    
    def get_customer_subscriptions(self, primarydomain: str) -> list:
        """
        Retrieve information about the subscriptions for the customer
        PARAMETERS:
            primarydomain: Customer's primary domain
        RETURNS:
            list. List containing subscriptions.
        """
        return self.__sendget(f'/customers/{primarydomain}/subscriptions').json()
    
    def get_customer_subscription(self, primarydomain: str, productcode: str) -> dict:
        """
        Retrieve information about a single subscription for a customer
        PARAMETERS:
            primarydomain: Customer's primary domain
            productcode: The product code.
        RETURNS:
            dict.
        """
        return self.__sendget(f'/customers/{primarydomain}/subscriptions/{productcode}').json()
    
    def get_cancellation_request(self, primarydomain: str, productcode: str):
        """
        Retrieve the cancellation request for a subscription.
        PARAMETERS:
            primarydomain: Customer's primary domain
            productcode: The product code.
        RETURNS:
            Dict.
        """
        return self.__sendget(f'/customers/{primarydomain}/subscriptions/{productcode}/cancellation-request').json()
    
    def create_customer(self,
                        primarydomain: str,
                        customername: str,
                        reference: str,
                        head_office_address: dict,
                        isactive: bool = True,
                        eu_vat_number: str = '',
                        iso_country_code: str = '',
                        admin_password: str = '',
                        billing_address: dict = {},
                        contacts: list = []
                        ):
        """
        Create a new customer.
        PARAMETERS:
            primarydomain: str. The primary domain for the customer. Must be unique within cascade.
            customername: str. Name of the customer.
            reference: str. Reference for the customer. Must be unique within cascade.
            isactive: bool. Whether the customer is active or not.
            eu_vat_number: str. Numberic VAT number for organisation.
            iso_country_code: str. 3 Letter ISO 3166-1 alpha-3 code for location of organisation. Defaults to GBR.
            admin_password: str. Password for customer. If not provided will be emailed.
            head_office_address: dict. Address dictionary (use make_address helper function)
            billing_address: dict. Address dictionary (use make_address helper function)
            contacts: list of contacts. (Use make_contact helper function). Send a type BillingContact to populate cascade gui.
        RETURNS:
            None. Exception will be raised on failure.
        """
        data = {
            'PrimaryDomain': primarydomain,
            'Name': customername,
            'Reference': reference,
            'IsActive': isactive,
            'HeadOfficeAddress': head_office_address,
        }
        if eu_vat_number:
            data['EUVATNumber'] = eu_vat_number
        if iso_country_code:
            data['IsoCountryCode'] = iso_country_code
        if admin_password:
            data['AdministratorPassword'] = admin_password
        if billing_address:
            data['BillingAddress'] = billing_address
        if contacts:
            data['Contacts'] = contacts
        self.__sendpost('/customers', data=data)
    
    def create_tenant(self, customer: str, tenantid: str):
        """
        Create a Microsoft tenant for the customer.
        PARAMETERS:
            customer: str. Customer's primary domain.
            tenantid: str. Required domain prefix, will be suffixed with onmicrosoft.com
                                eg. xxx, for xxx.onmicrosoft.com.
        RETURNS:
            None. Exception will be raised on error.
        """
        self.__sendpost(f'/customers/{customer}/MicrosoftTenant/{tenantid}.onmicrosoft.com')
    
    def create_subscription(self, customer: str, productinformation: dict):
        """
        Create a subscription for a customer.
        PARAMETERS:
            customer: primary domain for the customer.
            productinformation: dict. A dictionary containing the subscription information in the following format:
            {
                "Reference": "ref", # must be unique
                "Subscriptions": [ 
                    {
                        "ProductCode": "code",
                        "Quantity": 10,
                        "IsMandatory": True,
                        "Parameters": [ # optional
                            "key": "value"
                    } 
                    ]
                ]
            }
            EXAMPLE: {'Reference': '17112020', 'Subscriptions': [ {'ProductCode': 'R-UK-CSP-365BT-CMC', 'Quantity': 1 } ] }
        """
        self.__sendpost(f'/customers/{customer}/subscriptions', data=productinformation)
    
    def update_subscription(self, customer: str, productcode: str, newqty: int):
        """
        Change the quantity on a subscription
        PARAMETERS:
            customer: primary domain for the customer
            productcode: product code to be amended.
            newqty: quantity to change to.
        """
        # TODO: Doesn't Work.
        self.__sendpost(f'/customers/{customer}/subscriptions/{productcode}', data={'Quantity': newqty})
    
    def upgrade_subscription(self, customer:str, oldproductcode: str, newproductcode: str):
        """
        Upgrade a subscription to a new product code.
        PARAMETERS:
            customer: primary domain for the customer.
            oldproductcode: The current product code.
            newproductcode: The product code to upgrade to.
        """
        # Todo: Untested.
        self.__sendpost(f'/customers/{customer}/subscriptions/{oldproductcode}', data={'ProductCode': newproductcode})

    def submit_cancellation_request(self, customer: str, productcode: str, daterequested: str):
        """
        Request cancellation of a subscription on a customer's account.
        PARAMETERS:
            customer: The primary domain for the customer.
            productcode: The product code to cancel.
            daterequested: The date you would like the subscription to be cancelled in the format "YYYY-MM-DD HH:MM:SS"
        """
        self.__sendpost(f'/customers/{customer}/subscriptions/{productcode}/cancellation-request', data={'CancellationDateRequested': daterequested})
    
    def abort_cancellation_request(self, customer: str, productcode: str):
        """
        Aborts a cancellation request.
        PARAMETERS:
            customer: The primary domain for the customer.
            productcode: The product code to abort the cancellation for.        
        """
        self.__senddelete(f'/customers/{customer}/subscriptions/{productcode}/cancellation-request')
    
    def accept_mca(self,
                   customer: str, 
                   dateaccepted: str, 
                   firstname: str, 
                   surname: str, 
                   phone: str, 
                   email: str, 
                   line1: str, 
                   postcode: str, 
                   countryid: int):
        """
        Accept the MCA for a customer.
        PARAMETERS:
            customer: str. The customer's primary domain.
            dateaccepted: str. date/time in the format "2019-02-06T00:00:00"
            firstname: str. The customer's first name.
            surname: str. The customer's surname.
            phone: str. The customer's phone number.
            email: str. The customer's email address.
            line1: str. The first line of the customer's address.
            postcode: str. The post code of the customer's address.
            countryid: int. See inty API guide for full values. UK = 26.
        """
        data = {
            'DateAccepted': dateaccepted,
            'FirstName': firstname,
            'Surname': surname,
            'PhoneNumber': phone,
            'EmailAddress': email,
            'AddressLine1': line1,
            'Postcode': postcode,
            'CountryId': countryid,
            'AgreementUrl': 'https://aka.ms/customeragreement'
        }
        self.__sendpost(f'/customers/{customer}/McaAcceptance', data=data)

    def make_address(self, line1: str, city: str, postcode: str, line2: str = '', state: str = '') -> dict:
        """
        Make a dictionary from an address, as required by other API calls.
        PARAMETERS:
            line1: str. First line of the address.
            line2: str. OPTIONAL. Second line of the address.
            city: str. City of the address.
            state: str. State of the address. OPTIONAL unless in AU,CA,IT,JA,NL,ES,CH,US
            postcode: str. Post Code for the address
        RETURN:
            dict. Dictionary of values.
        """
        data = {
            'Line1': line1,
            'City': city,
            'Postcode': postcode
        }
        if line2:
            data['Line2'] = line2
        if state:
            data['State'] = state
        return data

    def make_contact(self, firstname: str, lastname: str, email: str, phone: str, contacttype: str, primary: bool) -> dict:
        """
        Make a dictionary from a contact, as required by other API calls.
        PARAMETERS:
            firstname: str. The contacts first name.
            lastname: str. The contacts last name.
            email: str. The contacts email address.
            phone: str. The contacts phone number.
            contacttype: str. One of: "ITContact", "BillingContact"
        RETURN:
            dict. Dictionary of values.
        """
        return {
            'FirstName': firstname,
            'LastName': lastname,
            'EmailAddress': email,
            'PhoneNumber': phone,
            'ContactType': contacttype,
            'IsPrimaryContact': primary
        }
    