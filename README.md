# abnormal
Reporistory for abnormal python a/b testing script

*** This scripts are on a testing phase, use at your own peril ***

Example of using the script to identify new js variables by using N number of proxies:

ubuntu@XXXXXX:~/abnormal$ python abnormal.py 
Got 20 proxies from cyber syndrome
Got 5 working proxies
Starting for target Instagram
Got 12 working observers
For https://www.instagram.com/
missing_total: {'qe-us-p-show_desktop_registration_upsell': 2}
diff_vars: {'qe-su-g': Set([u'rollout_20160325', u'test_20160322']), 'config-csrf_token': Set([u'rEdRg95anVlV4trW8sC12xkX49fYAsHt', u'SRe0vZ8bUMAk3NyrOzwZR15uko3eDU7w', u'6NL0EfdndvYwJCOGa2GfiZ3R7DlJil1L', u'b3qL91SbDS8Fz2X5eSebXIrqrvIIQ5hl', u'jb9k2Ert511dC2l4LB6LzRG99cfKgoM0', u's8bVw03bWCXoVLok5AQgrvzM4ZtAl589', u'mDNfzuC3qmrIHoCSjEEBUkz5VWvGQhuI', u'u9udxwNtE9xWtJL0ae5VltBLl7jLn41u', u'MQ6Q6GzJG9c03N12Mm7WnCiPgDSc54yG', u'XEBT7IPkroVSHdSvKadeyeHwkwW8xrld', u'liXFyX350sxPzPmqthZTMcvYvbypUQY8', u'Q5OwWVB9rs5TV5PMeBD0Ii93HWqY6Rkz']), 'qe-us-p-show_desktop_registration_upsell': Set([u'false', u'true']), 'qe-us-g': Set([u'', u'show_desktop_registration_upsell_03', u'show_desktop_registration_upsell_test_03']), 'country_code': Set([u'US', u'FR', u'DE', u'VN', u'GB', u'IN', u'RO'])}
--------------------------------------------------
