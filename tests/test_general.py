from abnormal import AB
import proxies

def get_proxies():
	return proxies.get_proxies()

def test_create_ab():
    ab = AB(get_proxies())
    assert ab

def test_get_proxies():
	working_proxies = get_proxies()
	assert len(working_proxies) > 100