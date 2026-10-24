"""Configure the running local demo for this fictional test. No credentials needed."""
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main():
    base = 'http://127.0.0.1:8000/api'
    with urlopen(base + '/state', timeout=10) as response:
        project = json.load(response)['project']
    backup = Path(__file__).with_name('previous_workspace_settings.json')
    if not backup.exists():
        backup.write_text(json.dumps({key: project.get(key) for key in
            ['name', 'owner', 'checks']}, indent=2) + '\n')
    body = {
        'name': 'Fictional referral workflow test',
        'owner': 'Manoj - demo reviewer',
        'checks': {
            'duplicate_entry': False,
            'missing_inputs': [],
            'unavailable_path_defined': True,
            'alert_owner': 'Front desk',
            'training_recorded': True,
            'required_region': 'US',
            'proposed_region': 'US',
            'local_validation_recorded': True,
            'required_operation': '',
            'declared_operations': [],
        },
    }
    request = Request(base + '/project', data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'}, method='PATCH')
    with urlopen(request, timeout=10) as response:
        json.load(response)
    print('Fictional referral-test settings saved. Previous approvals are now stale.')
    print('Next: upload 01 as current workflow, and 02 as proposed-app guide.')
    print('No LLM request was made. No API key was read or printed.')


if __name__ == '__main__':
    try:
        main()
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as error:
        print('Could not prepare the local workspace. Start npm run dev on port 8000 first.')
        print('Error type:', type(error).__name__)
        raise SystemExit(1)
