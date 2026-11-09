import sys
import pytest
from scripts.database import main


@pytest.mark.parametrize('environment,database,configured_host',[
    ('production','fashion_dev_safe','127.0.0.1'),
    ('development','fashion_dev_other','127.0.0.1'),
    ('development','fashion_dev_safe','remote.example.test'),
])
def test_reset_dev_rejects_unverified_target_before_connect(tmp_path,monkeypatch,environment,database,configured_host):
    config=tmp_path/'dev.local.env'
    config.write_text(f'APP_ENV={environment}\nDB_HOST={configured_host}\nDB_PORT=3308\nDB_NAME=fashion_dev_safe\nDB_USER=root\n',encoding='utf-8')
    monkeypatch.setattr(sys,'argv',['database.py','reset-dev','--database',database,
        '--host','127.0.0.1','--port','3308','--user','root','--config',str(config)])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code==2
