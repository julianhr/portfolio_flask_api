import pytest
import utils
import pdb


@pytest.fixture
def request_mock(mocker):
    return mocker.Mock()


class TestClampParamNum:
    default = 5
    min_val = 1
    max_val = 10


    def clamp(self, request, key):
        return utils.clamp_param_num(request, key, self.default, self.min_val, self.max_val)


    def test_clamping(self):
        key = 'test_key'

        request_mock.args = { key: 1 }
        assert self.clamp(request_mock, key) == 1

        request_mock.args = { key: 0 }
        assert self.clamp(request_mock, key) == 1

        request_mock.args = { key: 10 }
        assert self.clamp(request_mock, key) == 10

        request_mock.args = { key: 11 }
        assert self.clamp(request_mock, key) == 10

        request_mock.args = { key: 7 }
        assert self.clamp(request_mock, key) == 7


    def test_default(self):
        key = 'test_key'
        request_mock.args = {}
        assert self.clamp(request_mock, key) == self.default


    def test_exception_returns_default(self):
        key = 'test_key'
        request_mock.args = { key: 'hello' }
        assert self.clamp(request_mock, key) == self.default
