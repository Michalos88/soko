import requests
from pathlib import Path
import pickle

class StatefulClient(object):

    def __init__(
        self,
        api_name: str,
        state_dir: str = '../data/',
    ):
        self.api_name = api_name
        self.state_dir = Path(state_dir)
        self.state_path = self.state_dir/Path(self.api_name+'.pkl')

        try:
            self.state = self._load_state()
        except FileNotFoundError:
            print("Can't load state! Initializing new state.")
            self.state = self._init_state()
            self._save_state()


    def _load_state(self):
        IO = self.state_path.open('rb')
        state = pickle.load(IO)
        IO.close()
        return state

    def _init_state(self):
        state = dict()
        state['name'] = self.api_name
        state['state_path'] = self.state_path
        state['request_count'] = 0
        state['request_limit'] = 10000
        state['all_requests'] = list()
        return state

    def _save_state(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        IO = self.state_path.open('wb')
        pickle.dump(self.state, IO)
        IO.close()

    def _update_request_count(self):
        if self.state['request_count'] + 1 > self.state['request_limit']:
            err_msg = 'Max request count reached!'
            raise RuntimeError(err_msg)
        self.state['request_count'] += 1

    def get(self, **args):
        self._update_request_count()

        if args['url'] == "":
            res = None
        else:
            res = requests.get(**args)

        args['res'] = res
        self.state['all_requests'].append(args)
        self._save_state()
        return res

    def set_limit(self, limit):
        self.state['request_limit'] = limit
        self._save_state()

    def reset_state(self, yes):
        if yes is True:
            self.state = self._init_state()
            self._save_state()
