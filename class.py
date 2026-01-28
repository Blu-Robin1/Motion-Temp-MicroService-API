import logging

logging.basicConfig(level=logging.DEBUG,filename='log_demo.log',filemode='w')

# logging.debug("Debug") #Lease severe
# logging.info
# logging.warning
# logging.error
# logging.critical

try: 
    1/0
except ZeroDivisionError as e:
    logging.exception(e)