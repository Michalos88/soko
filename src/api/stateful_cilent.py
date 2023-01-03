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
        state['request_limit'] = None
        return state

    def _save_state(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        IO = self.state_path.open('wb')
        pickle.dump(self.state, IO)
        IO.close()

