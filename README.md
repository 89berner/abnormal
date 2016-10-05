# abnormal
Abnormal python a/b testing script

*** This scripts are on a testing phase, use at your own peril ***

This script requieres a working installation of phantomjs and opencv

Example of using the script to identify new or modified js variables by using N number of proxies:

```shell

ubuntu@XXXXXX:~/abnormal$ python abnormal.py --url https://www.instagram.com --proxies=100 --threads=10 -lINFO
INFO:root:Got 559 proxies from cyber syndrome
Starting for target https://www.instagram.com
INFO:root:Got 102 working observers
Report for https://www.instagram.com

Check missing_vars:

Variable Name                                     Amount
----------------------------------------------  --------
qe-su-g                                                1
qe-su-p-enabled                                        1
display_properties_server_guess-pixel_ratio            1
config-csrf_token                                      1
qe-notif-g                                             1
country_code                                           1
language_code                                          1
qe-us-p-display_reg_on_pill                           80
gatekeepers-sulgin                                     1
qe-discovery-g                                         1
hostname                                               1
qe-su_universe-p-on_login_page                        97
platform                                               1
qe-us-g                                                1
environment_switcher_visible_server_guess              1
entry_data-LandingPage                                 1
gatekeepers-cc                                         1
config-viewer                                          1
qe-us-p-use_continue_text                             83
qe-us_li-g                                             1
qe-profile-g                                           1
show_app_install                                       1
static_root                                            1
display_properties_server_guess-viewport_width         1
qe-su_universe-g                                       1

Check diff_vars:

Variable Name                   Possible value                              Amount
------------------------------  ----------------------------------------  --------
qe-su-g                         rollout_20160325                                45
qe-su-g                         test_20160322                                   54
qe-us-p-display_reg_on_pill     false                                           14
qe-us-p-display_reg_on_pill     true                                             6
qe-su_universe-p-on_login_page  login_only                                       1
qe-su_universe-p-on_login_page  show_signup                                      2
qe-us-g                                                                         41
qe-us-g                         logged_out_mobile_pill_upsell_control_02        14
qe-us-g                         continue_vs_signup_text_test_02                 17
qe-us-g                         continue_vs_signup_text_control_02              21
qe-us-g                         logged_out_mobile_pill_upsell_test_02            6
qe-su_universe-g                                                                96
qe-su_universe-g                test_show_signup_07                              2
qe-su_universe-g                control_login_only_07                            1
--------------------------------------------------
```
