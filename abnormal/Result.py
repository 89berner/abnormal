from tabulate import tabulate

class Result:
    def __init__(self, name, urls):
        self.name = name
        self.urls = {}
        for url in urls:
            self.urls[url] = UrlResult(url)

    def get(self,url):
        return self.urls[url]

    def get_array(self, url):
        return self.urls[url].as_array()

    def report(self):
        for url in self.urls:
            print "*" * 50
            print "For url: %s" % url
            self.print_table(url)

    def print_table(self, url):
        diff_results = self.urls[url].get_results_map()
        for check in diff_results:
            print "\n(%s) %s:\n" % (check, diff_results[check]['description'])
            columns = diff_results[check]['columns']
            results = diff_results[check]['results']
            
            print tabulate(results, headers=columns)

class UrlResult:
    def __init__(self, url):
        self.url = url
        self.missing_vars  = {}
        self.diff_vars     = {}
        self.missing_links = {}
        self.diff_images   = {}
        self.diff_marked_images = {}

    def set_missing_var(self,var_name):
        if var_name not in self.missing_vars:
            self.missing_vars[var_name] = 0
        self.missing_vars[var_name] += 1

    def set_missing_link(self,var_name):
        if link_name not in self.missing_links:
            self.missing_links[var_name] = 0
        self.missing_links[var_name] += 1

    #Set for each variable the different values and the occurances
    def set_diff_var(self,var_name,var_value):
        if var_name not in self.diff_vars:
            self.diff_vars[var_name] = {}
        if var_value not in self.diff_vars[var_name]:
            self.diff_vars[var_name][var_value] = 0 #[]
        self.diff_vars[var_name][var_value] += 1 #append

    def set_diff_images(self, md5, file_name):
        self.diff_images[md5] = file_name

    def set_diff_marked_images(self, md5, file_name):
        self.diff_marked_images[md5] = file_name

    def get_results_map(self):  
        results = {}

        results['diff_images'] = {}
        results['diff_images']['description'] = "Different captures"
        results['diff_images']['results'] = []
        results['diff_images']['columns'] = ['md5', 'Filename']
        for md5 in self.diff_images:
            results['diff_images']['results'].append([md5, self.diff_images[md5]])

        results['diff_marked_images'] = {}
        results['diff_marked_images']['description'] = "Different captures marked"
        results['diff_marked_images']['results'] = []
        results['diff_marked_images']['columns'] = ['md5', 'Filename']
        for md5 in self.diff_marked_images:
            results['diff_marked_images']['results'].append([md5, self.diff_marked_images[md5]])

        results['missing_links'] = {}
        results['missing_links']['description'] = "Links missing for some observers"
        results['missing_links']['results'] = []
        results['missing_links']['columns'] = ['Link', 'Amount']
        for link in self.missing_links:
            results['missing_links']['results'].append([link, self.missing_links[var]])

        results['missing_vars'] = {}
        results['missing_vars']['description'] = "Variables missing for some observers"
        results['missing_vars']['results'] = []
        results['missing_vars']['columns'] = ['Variable Name', 'Amount']
        for var in self.missing_vars:
            results['missing_vars']['results'].append([var, self.missing_vars[var]])

        results['diff_vars'] = {}
        results['diff_vars']['description'] = "Variables and their optional values for some observers"
        results['diff_vars']['results'] = []
        results['diff_vars']['columns'] = ['Variable Name', 'Possible value', 'Amount']
        blacklisted_vars = ['config-csrf_token','country_code']
        for var in self.diff_vars:
            if var in blacklisted_vars:
                continue
            for possible_value in self.diff_vars[var]:
                results['diff_vars']['results'].append([ var, possible_value, self.diff_vars[var][possible_value] ])

        return results