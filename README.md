# abnormal
Reporistory for abnormal python a/b testing script

*** This scripts are on a testing phase, use at your own peril ***

Example of using the script to identify new or modified js variables by using N number of proxies:

```shell

ubuntu@XXXXXX:~/abnormal$ python abnormal.py -u https://www.instagram.com --proxies=4 --threads=10
Got 16 proxies from cyber syndrome
Got 4 working proxies
Starting for target Instagram
Got 4 working observers
Report for Instagram
For https://www.instagram.com
missing_vars: {'qe-us-p-show_desktop_registration_upsell': 1}
diff_vars: {'config-csrf_token': Set([u'4plvTBzPzpq9CcrW0SQXJ3q05qQxhwXm', u'FevbvGVxjN0g7WBVdNcc2Xd2joJRmDVi', u'pgm3PTddpOZ6aAEcSgPSrfVvDfct5dfF', u'GXSeVojUbL0zVwKbu2oKkMVM6lrU5lV6']), 'qe-us-p-show_desktop_registration_upsell': Set([u'true', u'false']), 'qe-us-g': Set([u'', u'show_desktop_registration_upsell_test_05', u'show_desktop_registration_upsell_05']), 'country_code': Set([u'CA', u'DE', u'BR', u'TH'])}
--------------------------------------------------
```
